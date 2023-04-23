use std::{fs::File, io::Read};

use colored::Colorize;
use inquire::MultiSelect;
use unidiff::PatchSet;

use crate::openai;

pub fn diff(used_tokens: usize, context: usize) -> anyhow::Result<(String, usize)> {
    //read out file called diff.txt
    let mut file = File::open("diff.txt").unwrap();
    let mut contents = String::new();
    file.read_to_string(&mut contents).unwrap();

    let mut diff_tokens = openai::count_token(&contents).unwrap_or(0);

    while diff_tokens + used_tokens > context {
        let mut patch = PatchSet::new();
        patch.parse(&contents)?;
        println!(
            "{} {}",
            "The request is too long!".red(),
            format!(
                "The request is ~{} tokens long, while the maximum is {}.",
                used_tokens + diff_tokens,
                context
            )
            .bright_black()
        );

        let file_names: Vec<String> = patch.files().iter().map(|file| file.source_file.clone()).collect();
        let selected_file_names = MultiSelect::new(
            "Select the files you want to include in the diff:",
            file_names,
        )
        .prompt()?;

        let selected_files = selected_file_names.iter().map(|file_name| {
            patch
                .files()
                .iter()
                .find(|file| file.source_file == *file_name)
                .unwrap()
        });

        let mut new_contents = String::new();
        for file in selected_files {
            new_contents.push_str(&file.to_string());
        }

        diff_tokens = openai::count_token(&new_contents).unwrap_or(0);
    }

    Ok((contents, diff_tokens))
}
