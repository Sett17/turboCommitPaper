use std::process;

use colored::Colorize;

use unicode_segmentation::UnicodeSegmentation;

#[must_use]
pub fn count_lines(text: &str, max_width: usize) -> u16 {
    if text.is_empty() {
        return 0;
    }
    let mut line_count = 0;
    let mut current_line_width = 0;
    for cluster in UnicodeSegmentation::graphemes(text, true) {
        match cluster {
            "\r" | "\u{FEFF}" => {}
            "\n" => {
                line_count += 1;
                current_line_width = 0;
            }
            _ => {
                current_line_width += 1;
                if current_line_width > max_width {
                    line_count += 1;
                    current_line_width = cluster.chars().count();
                }
            }
        }
    }

    line_count + 1
}

pub fn choose_message(choices: Vec<String>) -> String {
    if choices.len() == 1 {
        return choices[0].clone();
    }
    let max_index = choices.len();
    let commit_index = match inquire::CustomType::<usize>::new(&format!(
        "Which commit message do you want to use? {}",
        "<ESC> to cancel".bright_black()
    ))
    .with_validator(move |i: &usize| {
        if *i >= max_index {
            Err(inquire::CustomUserError::from("Invalid index"))
        } else {
            Ok(inquire::validator::Validation::Valid)
        }
    })
    .prompt()
    {
        Ok(index) => index,
        Err(_) => {
            process::exit(1);
        }
    };
    choices[commit_index].clone()
}
