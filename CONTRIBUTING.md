# Contributing to MCP Training

Thank you for your interest in contributing to the MCP Training series! This project aims to provide educational resources for learning the Model Context Protocol through practical examples.

## How to Contribute

1. **Fork the Repository**: Start by forking the repository to your own GitHub account.

2. **Clone the Repository**: Clone your fork to your local machine.
   ```
   git clone https://github.com/YOUR-USERNAME/MCP-Training.git
   ```

3. **Create a Branch**: Create a branch for your contribution.
   ```
   git checkout -b feature/your-feature-name
   ```

4. **Make Your Changes**: Implement your changes, following the existing code style and structure.

5. **Test Your Changes**: Ensure your changes work as expected and don't break existing functionality.

6. **Commit Your Changes**: Commit your changes with a clear, descriptive message.
   ```
   git commit -m "Add feature: description of your changes"
   ```

7. **Push to Your Fork**: Push your changes to your fork on GitHub.
   ```
   git push origin feature/your-feature-name
   ```

8. **Submit a Pull Request**: Create a pull request from your branch to the main repository.

## Guidelines

- Follow the existing code style and structure
- Include appropriate documentation for new features
- Add comments explaining complex code sections
- Update README.md if necessary
- For new labs, follow the existing lab structure

## Lab Structure

When adding a new lab, please follow this structure:

```
Lab XX/
├── src/                        # Source code for server components (if applicable)
├── client.py or mcp_client.py  # MCP client implementation
├── server.py or [service].py   # MCP server implementation
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── README.md                   # Lab-specific documentation
└── .gitignore                  # Git ignore patterns
```

## License

By contributing to this project, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).