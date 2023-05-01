#import "template.typ": *
#show: project.with(
  title: "turbocommit",
  subtitle: "A Case Study in Applying Al to Streamline the Software Development Process",
  authors: (
    (name: "Raik Rohde", affiliation: "4380676"),
  ),
  abstract: [Conventional commit messages play a vital role in maintaining a clear and well-structured version control history in software development. However, writing informative and consistent commit messages can be challenging and time-consuming for developers. This paper presents and evaluates `turbocommit`, a novel tool that leverages the power of AI to generate conventional commit messages from git diffs. Utilizing the `gpt-3.5-turbo` language model, `turbocommit` aims to streamline the software development process by automating commit message creation and ensuring compliance with the Conventional Commits specification. The performance of AI-generated commit messages is compared with manually written ones in terms of accuracy, readability, and adherence to the specification. The evaluation methodology encompasses a mix of manual assessments and automated scoring systems, providing a comprehensive analysis of the effectiveness of AI-generated commit messages in a software development context.],
)

= Introduction
Commit messages play a crucial role in software development by maintaining a clear and well-structured version control history. However, developers often face difficulties in creating consistent and informative commit messages, which can hinder the efficiency of the development process. In this paper, we introduce `turbocommit`, a tool that harnesses the power of AI, specifically the `gpt-3.5-turbo` language model, to generate conventional commit messages from git diffs. The primary aim of `turbocommit` is to streamline the software development process by automating commit message creation and ensuring adherence to the Conventional Commits specification.

To demonstrate the effectiveness of `turbocommit`, this term paper presents the requirements and a comprehensive evaluation methodology. The evaluation includes a combination of manual assessments and automated scoring systems, comparing the performance of AI-generated commit messages with manually written ones using various metrics, such as accuracy, readability, and compliance with the Conventional Commits specification.

#include "theory.typ"
#include "method.typ"
#include "results.typ"
#include "discussion.typ"