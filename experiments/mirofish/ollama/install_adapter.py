"""Apply a checked, idempotent compatibility patch to a pinned checkout."""
import ast
from pathlib import Path
import shutil
import sys


def install(root):
    root = Path(root)
    changes = {
        'app/config.py': [
            ('("claude-cli", "codex-cli")', '("claude-cli", "codex-cli", "ollama")'),
            ("must be 'claude-cli' or 'codex-cli'", "must be 'claude-cli', 'codex-cli', or 'ollama'")],
        'app/utils/llm_client.py': [
            ('("claude-cli", "codex-cli")', '("claude-cli", "codex-cli", "ollama")'),
            ("Use 'claude-cli' or 'codex-cli'.", "Use 'claude-cli', 'codex-cli', or 'ollama'."),
            ('        last_error = None',
             '        if self.provider == "ollama":\n            from .romo_ollama import chat\n            return self._clean_content(chat(messages, temperature, max_tokens, response_format))\n        last_error = None')],
        'app/cli.py': [
            ('("claude-cli", "codex-cli")', '("claude-cli", "codex-cli", "ollama")'),
            ('return shutil.which(provider) is not None',
             'return shutil.which({"claude-cli": "claude", "codex-cli": "codex", "ollama": "ollama"}[provider]) is not None')]
    }
    prepared = {}
    for rel, replacements in changes.items():
        source = (root / rel).read_text(encoding='utf-8')
        for old, new in replacements:
            if new in source:
                continue
            if source.count(old) != 1:
                raise ValueError('Pinned upstream changed: ' + rel + ': ' + old)
            source = source.replace(old, new, 1)
        ast.parse(source)
        prepared[rel] = source
    for rel, source in prepared.items():
        (root / rel).write_text(source, encoding='utf-8')
    shutil.copyfile(Path(__file__).with_name('romo_ollama.py'), root / 'app/utils/romo_ollama.py')
    oasis = root / 'app/utils/oasis_llm.py'
    if oasis.exists():
        source = oasis.read_text(encoding='utf-8')
        old = "    model = config.get('llm_model') or provider"
        new = ('    if provider == "ollama":\n'
               '        from .romo_oasis_factory import create_local_oasis_model\n'
               '        return create_local_oasis_model()\n\n' + old)
        if new not in source:
            if source.count(old) != 1:
                raise ValueError('Pinned OASIS factory changed')
            source = source.replace(old, new, 1)
        ast.parse(source)
        oasis.write_text(source, encoding='utf-8')
        shutil.copyfile(Path(__file__).with_name('romo_oasis_factory.py'), root / 'app/utils/romo_oasis_factory.py')


if __name__ == '__main__':
    install(sys.argv[1])
    print('OLLAMA_ADAPTER_INSTALLED; no model call performed')
