import os
import json


class DotDict(dict):
    """
    Class representing a dictionary with dot notation access.
    """
    def __getattr__(self, attr):
        value = self.get(attr)
        if isinstance(value, dict):
            return NestedDict(value)
        return value

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, item):
        if item in self:
            del self[item]

class Event(NestedDict):
    """
    Class representing the event details of a GitHub workflow.
    """
    owner: str = ''
    """Owner of the repository. Example: 'octocat'"""
    
    repo: str = ''
    """Name of the repository. Example: 'Hello-World'"""
    
    number: int = 0
    """Number of the issue. Example: 1347"""

class Context:
    """
    Class representing the context of a GitHub workflow.
    """

    payload: dict = {}
    """
    Webhook payload object that triggered the workflow.
    Example: {'action': 'opened', 'issue': {'url': 'https://api.github.com/repos/octocat/Hello-World/issues/1347', 'number': 1347}}
    """
    
    event_name: str = ''
    """Name of the event that triggered the workflow. Example: 'push'"""
    
    sha: str = ''
    """SHA of the commit that triggered the workflow. Example: 'abc123'"""
    
    ref: str = ''
    """Git ref or branch that triggered the workflow. Example: 'refs/heads/feature-branch'"""
    
    workflow: str = ''
    """Name of the workflow. Example: 'Build and Test'"""
    
    action: str = ''
    """Identifier of the action. Example: 'opened'"""
    
    actor: str = ''
    """Login of the user that initiated the workflow. Example: 'octocat'"""
    
    job: str = ''
    """Identifier of the job. Example: 'build'"""
    
    run_attempt: int = 0
    """Number of the current attempt of the job. Example: 1"""
    
    run_number: int = 0
    """Number of the current run of the workflow. Example: 42"""
    
    run_id: int = 0
    """Unique identifier of the run. Example: 1234567890"""
    
    api_url: str = 'https://api.github.com'
    """URL of the GitHub API. Example: 'https://api.github.com'"""
    
    server_url: str = 'https://github.com'
    """URL of the GitHub server. Example: 'https://github.com'"""
    
    graphql_url: str = 'https://api.github.com/graphql'
    """URL of the GitHub GraphQL API. Example: 'https://api.github.com/graphql'"""
    
    def __init__(self):
        """
        Initialize the context from the environment.
        """
        for field in self.__dict__.keys():
            if not field.startswith('_') and not callable(getattr(self, field)):
                env_var = 'GITHUB_' + field.upper()
                default_value = getattr(self, field)
                setattr(self, field, os.getenv(env_var, default_value))

        self.payload = self._get_payload()

    @staticmethod
    def _get_payload() -> dict:
        """
        Get the webhook payload object that triggered the workflow.
        """
        event_path = os.getenv('GITHUB_EVENT_PATH')
        if event_path and os.path.exists(event_path):
            with open(event_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}

    @property
    def issue(self) -> Event:
        """
        Get the issue details from the payload.
        Returns an Event object with the owner, repo, and number of the issue.
        """
        number = self.payload.get('issue', self.payload.get('pull_request', self.payload)).get('number')
        return Event(**self.repo, number=number)

    @property
    def repo(self) -> dict:
        """
        Get the repository details from the payload.
        Returns a dictionary with the owner and name of the repository.
        """
        repository = os.getenv('GITHUB_REPOSITORY')
        if repository:
            owner, repo = repository.split('/')
            return {'owner': owner, 'repo': repo}
        elif 'repository' in self.payload:
            return {
                'owner': self.payload['repository']['owner']['login'],
                'repo': self.payload['repository']['name']
            }
        else:
            raise ValueError("context.repo requires a GITHUB_REPOSITORY environment variable like 'owner/repo'")
