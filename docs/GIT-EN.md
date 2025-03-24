# Git Commit Guidelines

In order to ensure that the history of the codebase is clear and well-organized, and to avoid confusion, we have established the following Git commit guidelines. Every commit should follow these rules so that team members can better understand the commit history and the purpose of code changes.

## Commit Message Format

Each Git commit message should follow this format:

```text
<type>(<scope>): <short description>
<detailed description>
<related issue/task link>
```

### 1. Type

The type of the commit should be one of the following:

- **feat**: A new feature (feature)
- **fix**: A bug fix
- **docs**: Documentation updates
- **style**: Code style changes (no changes to the code logic)
- **refactor**: Code refactoring (changes that neither fix a bug nor add a feature)
- **perf**: Performance improvements
- **test**: Adding or modifying tests
- **chore**: Other miscellaneous tasks (build process, tooling, dependencies management, etc.)
- **ci**: Continuous integration-related changes
- **build**: Changes related to the build process (e.g., gulp, webpack)
- **revert**: Reverts a previous commit

### 2. Scope

The scope refers to the part of the code or functionality that the commit affects, typically written in lowercase. For example: `login`, `api`, `ui`, `config`, etc.

If the commit doesn’t involve a specific scope, this part can be omitted.

### 3. Short Description

The short description should be concise and clear, no more than 50 characters. It should use **imperative verbs** to describe the changes made.

### 4. Detailed Description

The detailed description should provide further explanation of the commit, including context, problem-solving, or other important information. If the commit message is simple, this part can be omitted.

Each line of the detailed description should not exceed 72 characters.

### 5. Related Issue or Task

If the commit is related to a specific issue or task, include the issue number or task link at the end of the commit message. For example:

#### `Closes #123 Fixes #456 See #789 for more details`

#### Commit Examples

##### Example 1
```text
feat(api): add user authentication
 - Implement JWT authentication
 - Add login and logout endpoints
 - Update user model to store tokens
```

##### Example 2
```text
fix(ui): resolve button misalignment issue
 - Fixes the button alignment issue in the header section
 - Update CSS for button styling
See #112 for discussion

```
##### Example 3
```text
docs(readme): update installation instructions
- Add step-by-step guide for setting up the development environment
```

## Commit Best Practices

1. **Keep commits small**: Each commit should contain a single change. Avoid submitting large batches of changes in a single commit.
2. **Avoid committing generated files**: Unless absolutely necessary, do not commit generated files, dependencies, etc., to version control.
3. **Commit frequently**: Frequently committing helps maintain a clean version history and makes it easier to trace changes over time.

## Enforced Guidelines

In order to improve development efficiency and code quality, all commits must adhere to these guidelines. Commits that do not follow these guidelines will be rejected.

## Conclusion

The above are our team’s Git commit guidelines. Please make sure to follow them when committing code. Standardized commits not only help team members quickly understand code changes but also improve the maintainability of the project.
