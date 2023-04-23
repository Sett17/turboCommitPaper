use std::{
    fmt::{self},
    fs::File,
    io::Read,
};

use colored::Colorize;
use inquire::MultiSelect;
use unidiff::{PatchSet, PatchedFile};

use crate::openai;

#[derive(Debug, PartialEq)]
struct DiffFile {
    source_file: String,
    target_file: String,
}

impl fmt::Display for DiffFile {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} -> {}", self.source_file, self.target_file)
    }
}

impl From<&PatchedFile> for DiffFile {
    fn from(value: &PatchedFile) -> Self {
        DiffFile {
            source_file: value.source_file.clone(),
            target_file: value.target_file.clone(),
        }
    }
}

impl PartialEq<&PatchedFile> for DiffFile {
    fn eq(&self, other: &&PatchedFile) -> bool {
        self.source_file == other.source_file && self.target_file == other.target_file
    }
}

pub fn diff(used_tokens: usize, context: usize) -> anyhow::Result<(String, usize)> {
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

        let file_names: Vec<DiffFile> = patch
            .files()
            .iter()
            .map(|file| DiffFile::from(file))
            .collect();
        let selected_file_names = MultiSelect::new(
            "Select the files you want to include in the diff:",
            file_names,
        )
        .prompt()?;

        let selected_files = selected_file_names.iter().map(|file_names| {
            patch
                .files()
                .iter()
                .find(|file| *file_names == *file)
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
