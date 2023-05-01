= Methods

== Gathering Data

Several GitHub repositories were identified as suitable sources of commit messages.
These repositories include: taxonomy @shadcnShadcnTaxonomy2023, resume @dcyouDcyouResume2022, and kotlin-faker @serpro69Serpro69Kotlinfaker2023. While kotlin-faker does not adhere to Conventional Commits, its commit messages maintain a consistent structure. The specific functionality of these repositories is not vital for the evaluation.

All selected repositories have multiple contributors, which increases the diversity of the commit messages. A Python script was utilized to traverse all commits in these repositories, extracting both the commit message and the corresponding git diff. These data points were then stored in an SQLite database for further processing. Commit messages authored by bots or merge commits were filtered out and placed in a separate table within the same SQLite database.

From the three repositories using Conventional Commits, approximately 100 non-filtered commits were collected for each (99 from taxonomy, and ??? from resume). To maintain a balanced evaluation, only ??? random commits from kotlin-faker were included. This approach ensures that the overall evaluation is not disproportionately influenced by the kotlin-faker repository.

== Implementation

`turbocommit` works by analyzing the changes in a code repository, sending the relevant information along with a well-crafted system message to the `gpt-3.5-turbo` API, which then returns a defined um number of suggested commit messages. It is important to note that the `gpt-3.5-turbo` language model has a token limit of 4096 tokens; therefore, if a diff is too large, it must be split so that not all staged files are included in the diff.

In order to adapt `turbocommit` for this paper, several modifications were made:

+ Instead of using libgit2 to obtain the diff, the adapted version reads the diff from a diff.txt file.
+ Rather than prompting the user to choose what to do with the generated message (e.g., commit, edit and commit), the adapted version writes the message to an output.txt file for further analysis.
+ For the sake of time efficiency, only one message is generated for each commit, as opposed to the typical process where users can generate multiple messages and choose the best one.

These adaptations allow `turbocommit` to function effectively within the scope of this paper while still maintaining its core capabilities as a commit message generation tool.

== Evaluation

Two Python scripts were developed to facilitate the evaluation process, with significant assistance from generative AI tools, specifically GPT-4. These tools played a crucial role in authoring the scripts, under careful guidance and supervision.

The first script generates a new table within the SQLite database and iterates through all human-authored commits. It then calculates the scores for each commit based on the metrics outlined in the theory section of this paper.

The second script is responsible for the manual accuracy scoring process. It iterates through all partially scored commits in random order. For each commit, the script displays the git diff, followed by either the human-written or AI-generated commit message. The evaluator manually inputs a score for the commit message, and then the script reveals the other message, which is also scored.

In the interest of brevity, the complete details and workings of the scripts have not been included in this paper.