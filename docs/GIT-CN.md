# Git 提交规范

为了确保代码库的历史清晰、规范化，避免混乱，我们制定了以下的 Git 提交规范。每次提交都应该遵循这些规则，以便团队成员可以更好地理解提交历史和代码变更的目的。

## 提交信息格式

每个 Git 提交信息应该遵循以下格式：

```text
<类型>(<范围>):<简短描述>
<详细描述>
<影响的Issue/任务链接>
```


### 1. 类型（Type）

提交的类型应该用下列之一：

- **feat**: 新功能（feature）
- **fix**: 修复 bug
- **docs**: 文档更新
- **style**: 代码格式（不影响代码运行的变动）
- **refactor**: 代码重构（既不是修复 bug，也不是添加新功能的变动）
- **perf**: 性能优化
- **test**: 添加或修改测试
- **chore**: 其他杂项工作（构建流程、工具、依赖管理等）
- **ci**: 持续集成相关的变动
- **build**: 与构建相关的变动（例如：gulp、webpack）
- **revert**: 撤销先前的提交

### 2. 范围（Scope）

范围是指影响的模块或功能区域，通常用小写字母表示。例如：`login`, `api`, `ui`, `config` 等。

如果提交不涉及某个特定范围，可以省略这一部分。

### 3. 简短描述

简短描述应该简洁明了，最多不超过 50 个字符。应该使用 **动词原形** 来描述变更的内容。

### 4. 详细描述

详细描述应该用来详细说明提交的背景、解决的问题和其他重要信息。如果提交信息较简单，可以省略这一部分。

详细描述的每行不应超过 72 个字符。

### 5. 关联 Issue 或任务

如果提交与某个 Issue 或任务相关联，应在提交信息的末尾加上 Issue 的编号或任务链接。例如：

#### `Closes #123 Fixes #456 See #789 for more details`
#### 提交示例
##### 示例 1
```text
feat(api): add user authentication
 - Implement JWT authentication
 - Add login and logout endpoints
 - Update user model to store tokens
```

##### 示例 2
```text
fix(ui): resolve button misalignment issue
 - Fixes the button alignment issue in the header section
 - Update CSS for button styling
See #112 for discussion
```

##### 示例 3
```text
docs(readme): update installation instructions
- Add step-by-step guide for setting up the development environment
```


## 提交实践建议

1. **保持提交粒度小**：每个提交应该包含单一的变更内容，避免一次性提交大量修改。
2. **避免提交生成文件**：除非确有必要，否则不要将编译后的文件、依赖项等提交到版本控制中。
3. **频繁提交**：在开发过程中频繁提交，可以保持版本控制的清晰和可追溯性。

## 强制规范

为了提高开发效率和代码质量，所有提交必须遵循以上规范。如果提交信息不符合规范，提交将被拒绝。

## 结语

以上是我们团队的 Git 提交规范，请大家在提交代码时务必遵守。规范化的提交不仅能帮助团队成员快速理解代码变更，还能提高项目的可维护性。
