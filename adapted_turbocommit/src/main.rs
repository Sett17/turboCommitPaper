use colored::Colorize;

use openai::{Message, Model};

use std::{env, fs::File, io::Write, process};

mod adaptions;
mod animation;
mod openai;
mod util;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let Ok(api_key) = env::var("OPENAI_API_KEY") else {
        println!("{} {}", "OPENAI_API_KEY not set.".red(), "Refer to step 3 here: https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety".bright_black());
        process::exit(1);
    };

    let extra = env::args().skip(1).collect::<Vec<String>>().join(" ");

    let system_len = openai::count_token(SYSTEM_MSG).unwrap_or(0);
    let extra_len = 0;

    let (diff, diff_tokens) =
        adaptions::diff(system_len + extra_len, Model::Gpt35Turbo.context_size())?;

    let prompt_tokens = system_len + extra_len + diff_tokens;

    let mut messages = vec![
        Message::system(String::from(SYSTEM_MSG)),
        Message::user(diff),
    ];

    if !extra.trim().is_empty() {
        messages.push(Message::user(format!(
            "extra user explanation: '{}'",
            extra
        )));
    }

    let choices = openai::Request::new(Model::Gpt35Turbo.to_string(), messages, 3, 0.78, 0.0)
        .execute(api_key, false, Model::Gpt35Turbo, prompt_tokens)
        .await?;

    let chosen_message = util::choose_message(choices);

    let mut file = File::create("output.txt").unwrap();
    file.write_all(chosen_message.as_bytes()).unwrap();
    println!(
        "{} {}",
        "Message written to output.txt".green(),
        "🎉".bright_black()
    );

    Ok(())
}

const SYSTEM_MSG: &str = r#"As an AI that only returns conventional commits, you will receive input from the user in the form of a git diff of all staged files. The user may provide extra information to explain the change. Focus on the why rather than the what and keep it brief. You CANNOT generate anything that is not a conventional commit and a commit message only has 1 head line and at most 1 body.
Ensure that all commits follow these guidelines

- Commits must start with a type, which is a noun like feat, fix, refactor, etc., followed by an optional scope, an optional ! for breaking changes, and a required terminal colon and space
- Use feat for new features and fix for bug fixes
- You may provide a scope after a type. The scope should be a noun describing a section of the codebase, surrounded by parentheses
- After the type/scope prefix, include a short description of the code changes. This description should be followed immediately by a colon and a space
- You may provide a longer commit body after the short description. Body should start one blank line after the description and can consist of any number of newline-separated paragraphs

Example
feat: add a new feature

This body describes the feature in more detail";

// const SYSTEM_MSG: &str = r#"AI: gen conv commit-msg. Input: git diff staged files, context, user instr. Task: focus purpose, brief, clear. Output: 1 msg (1 headline, ≤1 body) ONLY.
// Commit-msg guidelines:
// 1. Start: type (feat, fix, refactor, chore, etc.), opt. scope, opt. ! (breaking), req. colon+space.
// 2. feat=new features, fix=bug fixes, etc.
// 3. Scope: codebase section, in ().
// 4. After type/scope: concise desc, colon+space.
// 5. Longer body: blank line after desc.

// Multi-changes: 1 msg, concise. 📝Include all crucial changes. ⚠️ ONLY headline & body in output. No extra notes/comments/content.

// ```example
// feat: add new feature

// feature detail
// ```"#;
