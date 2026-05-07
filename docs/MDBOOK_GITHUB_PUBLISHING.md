# mdBook / GitHub 发布说明

## 本地检查

```bash
mdbook serve
```

## GitHub 发布

1. 新建 GitHub 仓库；
2. 提交本包根目录；
3. 运行 `mdbook build`；
4. 使用 GitHub Pages 发布 `book/` 目录或配置 GitHub Actions。

## Mermaid

当前 `book.toml` 未默认启用 Mermaid preprocessor，避免用户未安装插件导致构建失败。如需渲染，请额外安装 `mdbook-mermaid`。
