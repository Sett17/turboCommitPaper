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

    let system_len = openai::count_token(SYSTEM_MSG).unwrap_or(0);
    let extra_len = 0;

    let (diff, diff_tokens) =
        adaptions::diff(system_len + extra_len, Model::Gpt35Turbo.context_size())?;

    let prompt_tokens = system_len + extra_len + diff_tokens;

    let messages = vec![
        Message::system(String::from(SYSTEM_MSG)),
        Message::user(diff),
    ];

    let choices = openai::Request::new(Model::Gpt35Turbo.to_string(), messages, 3, 0.8, 0.0)
        .execute(api_key, false, Model::Gpt35Turbo, prompt_tokens)
        .await?;

    let chosen_message = util::choose_message(choices);

    let mut file = File::create("output.txt").unwrap();
    file.write_all(chosen_message.as_bytes()).unwrap();
    println!(
        "{} {}",
        "Output written to output.txt".green(),
        "🎉".bright_black()
    );

    Ok(())
}

const SYSTEM_MSG: &str = r#"AI: gen conv commit-msg. Input: git diff staged files, context, user instr. Task: focus purpose, brief, clear. Output: 1 msg (1 headline, ≤1 body) ONLY.
Commit-msg guidelines:
1. Start: type (feat, fix, chore, etc.), opt. scope, opt. ! (breaking), req. colon+space.
2. feat=new features, fix=bug fixes, etc.
3. Scope: codebase section, in ().
4. After type/scope: concise desc, colon+space.
5. Longer body: blank line after desc.

Multi-changes: 1 msg, concise. 📝Include all crucial changes. ⚠️ ONLY headline & body in output. No extra notes/comments/content.

```example
feat: add new feature

feature detail
```"#;
