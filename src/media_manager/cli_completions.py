from __future__ import annotations

import argparse
import os
import sys


SHELL_SCRIPTS = {
    "bash": r'''_media_manager_completions() {
    local cur prev words cword
    _init_completion || return

    local commands="app cleanup duplicates doctor inspect organize people rename runs stats trip undo watch workflow config"
    local subcommands=""

    case "${prev}" in
        media-manager)
            COMPREPLY=($(compgen -W "${commands}" -- "${cur}"))
            return
            ;;
        config)
            COMPREPLY=($(compgen -W "--show --set --get --unset --reset --value --default --json --help" -- "${cur}"))
            return
            ;;
        watch)
            COMPREPLY=($(compgen -W "--source --target --pattern --interval --move --non-recursive --include-hidden --help" -- "${cur}"))
            return
            ;;
        stats)
            COMPREPLY=($(compgen -W "--source --non-recursive --include-hidden --top --json --help" -- "${cur}"))
            return
            ;;
    esac

    # Default: suggest --json --quiet --help and filesystem
    local common_flags="--json --quiet --help"
    COMPREPLY=($(compgen -W "${common_flags}" -- "${cur}"))
    COMPREPLY+=($(compgen -f -- "${cur}"))
}

complete -F _media_manager_completions media-manager
''',
    "zsh": r'''#compdef media-manager

_media_manager() {
    local -a commands
    commands=(
        'app:Start the desktop application'
        'cleanup:Clean up leftover files after organize'
        'config:Manage media-manager configuration'
        'duplicates:Find and manage duplicate files'
        'doctor:Validate workflow inputs'
        'inspect:Inspect media file metadata'
        'organize:Organize media files into a target structure'
        'people:Manage people and face recognition'
        'rename:Rename media files'
        'runs:Manage history and past runs'
        'stats:Print library statistics'
        'trip:Manage trip-based organization'
        'undo:Undo previous operations'
        'watch:Watch a directory for changes'
        'workflow:Run guided workflows'
    )

    _arguments \
        '--json[Machine-readable JSON output]' \
        '--quiet[Suppress non-error output]' \
        '--version[Show version]' \
        '--help[Show help]' \
        '1:command:{_describe command commands}' \
        '*::args:_normal'
}

_media_manager
''',
    "fish": r'''function __fish_media_manager_commands
    echo app\t"Start the desktop application"
    echo cleanup\t"Clean up leftover files after organize"
    echo config\t"Manage media-manager configuration"
    echo duplicates\t"Find and manage duplicate files"
    echo doctor\t"Validate workflow inputs"
    echo inspect\t"Inspect media file metadata"
    echo organize\t"Organize media files into a target structure"
    echo people\t"Manage people and face recognition"
    echo rename\t"Rename media files"
    echo runs\t"Manage history and past runs"
    echo stats\t"Print library statistics"
    echo trip\t"Manage trip-based organization"
    echo undo\t"Undo previous operations"
    echo watch\t"Watch a directory for changes"
    echo workflow\t"Run guided workflows"
end

complete -c media-manager -f
complete -c media-manager -s h -l help -d "Show help"
complete -c media-manager -l json -d "Machine-readable JSON output"
complete -c media-manager -l quiet -d "Suppress non-error output"
complete -c media-manager -l version -d "Show version"
complete -c media-manager -n "not __fish_seen_subcommand_from (__fish_media_manager_commands | string split '\n')" -a "(__fish_media_manager_commands)"
complete -c media-manager -n "__fish_seen_subcommand_from config" -a "--show --set --get --unset --reset --value --default --json --help"
complete -c media-manager -n "__fish_seen_subcommand_from watch" -a "--source --target --pattern --interval --move --non-recursive --include-hidden --help"
complete -c media-manager -n "__fish_seen_subcommand_from stats" -a "--source --non-recursive --include-hidden --top --json --help"
complete -c media-manager -n "__fish_seen_subcommand_from organize" -a "--source --target --pattern --copy --move --apply --non-recursive --include-hidden --include-associated-files --conflict-policy --include-pattern --exclude-pattern --show-files --json --report-json --review-json --run-log --journal --history-dir --run-dir --exiftool-path --resume --checkpoint --consolidate-leftovers --leftover-dir-name --help"
complete -c media-manager -n "__fish_seen_subcommand_from duplicates" -a "--source --show-groups --similar-images --show-similar-groups --show-similar-review --similar-policy --similar-threshold --export-similar-decisions --import-similar-decisions --save-similar-session --load-similar-session --show-similar-decisions --show-similar-plan --similar-apply --policy --mode --include-pattern --media-kind --include-extension --exclude-extension --list-supported-formats --exclude-pattern --target --load-session --import-decisions --export-decisions --save-session --show-decisions --show-unresolved --show-plan --json --json-report --report-json --review-json --run-log --journal --history-dir --run-dir --apply --yes --help"
''',
    "powershell": r'''$commands = @(
    [System.Management.Automation.CompletionResult]::new('app', 'app', 'ParameterValue', 'Start the desktop application'),
    [System.Management.Automation.CompletionResult]::new('cleanup', 'cleanup', 'ParameterValue', 'Clean up leftover files after organize'),
    [System.Management.Automation.CompletionResult]::new('config', 'config', 'ParameterValue', 'Manage media-manager configuration'),
    [System.Management.Automation.CompletionResult]::new('duplicates', 'duplicates', 'ParameterValue', 'Find and manage duplicate files'),
    [System.Management.Automation.CompletionResult]::new('doctor', 'doctor', 'ParameterValue', 'Validate workflow inputs'),
    [System.Management.Automation.CompletionResult]::new('inspect', 'inspect', 'ParameterValue', 'Inspect media file metadata'),
    [System.Management.Automation.CompletionResult]::new('organize', 'organize', 'ParameterValue', 'Organize media files into a target structure'),
    [System.Management.Automation.CompletionResult]::new('people', 'people', 'ParameterValue', 'Manage people and face recognition'),
    [System.Management.Automation.CompletionResult]::new('rename', 'rename', 'ParameterValue', 'Rename media files'),
    [System.Management.Automation.CompletionResult]::new('runs', 'runs', 'ParameterValue', 'Manage history and past runs'),
    [System.Management.Automation.CompletionResult]::new('stats', 'stats', 'ParameterValue', 'Print library statistics'),
    [System.Management.Automation.CompletionResult]::new('trip', 'trip', 'ParameterValue', 'Manage trip-based organization'),
    [System.Management.Automation.CompletionResult]::new('undo', 'undo', 'ParameterValue', 'Undo previous operations'),
    [System.Management.Automation.CompletionResult]::new('watch', 'watch', 'ParameterValue', 'Watch a directory for changes'),
    [System.Management.Automation.CompletionResult]::new('workflow', 'workflow', 'ParameterValue', 'Run guided workflows')
)

Register-ArgumentCompleter -Native -CommandName media-manager -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    $tokens = $commandAst.CommandElements
    $globalFlags = @('--json', '--quiet', '--help', '--version')

    if ($tokens.Count -eq 1) {
        $globalFlags | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterName', 'Global flag')
        }
        $commands | Where-Object { $_.CompletionText -like "$wordToComplete*" }
    }

    $command = $null
    for ($i = 1; $i -lt $tokens.Count; $i++) {
        if ($tokens[$i].ParameterName -eq $null -and $tokens[$i].Value -in $commands.CompletionText) {
            $command = $tokens[$i].Value
            break
        }
    }

    $flagCompletions = {
        param($flags)
        $flags | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterName', 'Flag')
        }
    }

    switch ($command) {
        'config' { & $flagCompletions @('--show', '--set', '--get', '--unset', '--reset', '--value', '--default', '--json', '--help') }
        'watch'  { & $flagCompletions @('--source', '--target', '--pattern', '--interval', '--move', '--non-recursive', '--include-hidden', '--help') }
        'stats'  { & $flagCompletions @('--source', '--non-recursive', '--include-hidden', '--top', '--json', '--help') }
    }
}
''',
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager completions",
        description="Generate shell completion scripts for media-manager.",
    )
    parser.add_argument(
        "shell",
        choices=sorted(SHELL_SCRIPTS.keys()),
        help="Target shell for completion script.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.shell not in SHELL_SCRIPTS:
        print(f"Error: unsupported shell '{args.shell}'", file=sys.stderr)
        return 1

    script = SHELL_SCRIPTS[args.shell]
    use_json = os.environ.get("MEDIA_MANAGER_JSON") == "1"

    if use_json:
        import json
        print(json.dumps({"shell": args.shell, "script": script}))
    else:
        print(script)
    return 0
