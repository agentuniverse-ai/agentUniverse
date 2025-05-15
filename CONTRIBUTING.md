**🎈🎈🎈 Welcome to agentUniverse！🎉🎉🎉**  
Thank you for your interest in agentUniverse and your willingness to contribute. We welcome you to join the agentUniverse community family. As an open-source project in the field of artificial intelligence, your contributions are important to the development and improvement of our project. We welcome all types of contributions, such as introducing new features, fixing code issues, improving documentation, submitting issues, and adding examples.

### Communicate with Us
If you have any ideas or questions related to contributions, feel free to reach out to us in advance. You can communicate through the [issue](https://github.com/antgroup/agentUniverse/issues) section of the agentUniverse project, send us an email, or join our community for discussions. For more detailed communication methods, please refer to the [Contact Information](docs/guidebook/en/Contact_Us.md)。

### Guidelines
#### Contributing to the Code & Docs
The contribution process for code and documentation in this project fully follows the standard procedures of the GitHub community. You can refer to the official GitHub [Fork-and-Pull-Request](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project) documentation for detailed operational steps.

During the commit submission process, this project follows part of the Angular git commit conventions, and you are required to tag the corresponding type in your commit messages.

Here is the list of commit types:
* feat: New feature (e.g., feat: add Agent Template feature)
* fix: Bug fix (e.g., fix: fix memory leak in framework core)
* docs: Documentation update (e.g., docs: update agent usage guide documentation)
* refactor: Code refactoring that does not involve changes to functionality (e.g., refactor: refactor knowledge processing module code)
* test: Testing-related submissions or tools (e.g., test: add unit tests for agent loading module)
* chore: Other changes (e.g., chore: replace project icon image)

##### Guideline for PR
During the PR submission process, we follow the aforementioned commit types. You can choose the type as a PR label based on the main content of your submission.

Please ensure that you meet the following requirements when submitting your PR:

- Read and understand the requirements outlined in the [Contributor Guidelines](https://github.com/antgroup/agentUniverse/blob/master/CONTRIBUTING.md).
- Check for any duplicate features related to this request and communicated with the project maintainers.
- Accept the suggestion of the maintainers to make changes to or close this PR.
- Submit the test files and can provide screenshots of the test results (required for feature or bug fixes).
- Add or modified the documentation related to this PR.
- Add examples and notes if needed.
- Carefully fill out the PR request, including assigning maintainers, providing a detailed description of the PR content, and including necessary explanations and screenshots.

#### Guideline for development
We recommend following the [python PEP8](https://peps.python.org/pep-0008/) and [Google Python Style](https://google.github.io/styleguide/pyguide.html) guidelines.

If you are new in Python language, there is no need to feel pressured by these standards; just focus on the following basic guidelines:

##### Naming Conventions
Refer to the [Naming Styles](https://peps.python.org/pep-0008/#naming-conventions) in PEP8.

##### Commenting Standards
Provide comments in the following sample format, including function descriptions, Args parameters, Returns values, and Raises error information, etc.
```python
def connect_to_next_port(self, minimum: int) -> int:
    """Connects to the next available port.

    Args:
      minimum: A port value greater or equal to 1024.

    Returns:
      The new minimum port.

    Raises:
      ConnectionError: If no available port is found.
    """
    if minimum < 1024:
      # Note that this raising of ValueError is not mentioned in the doc
      # string's "Raises:" section because it is not appropriate to
      # guarantee this specific behavioral reaction to API misuse.
      raise ValueError(f'Min. port must be at least 1024, not {minimum}.')
    port = self._find_next_open_port(minimum)
    if port is None:
      raise ConnectionError(
          f'Could not connect to service on port {minimum} or higher.')
    # The code does not depend on the result of this assert.
    assert port >= minimum, (
        f'Unexpected port {port} when minimum was {minimum}.')
    return port
```

#### Contributing to article & examples
If you have used the agentUniverse project and are satisfied with it, we welcome you to share your case studies in the project community or on any media platform. We will periodically hold community events to comment, encourage, and promote outstanding cases and developers.
