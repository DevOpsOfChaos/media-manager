# Bash completion for media-manager CLI
_media_manager_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Top-level subcommands
    local subcommands="app cleanup duplicates doctor inspect organize people rename runs trip undo workflow"

    if [[ ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "${subcommands} --version --help" -- ${cur}) )
        return 0
    fi

    # Default to file completion
    COMPREPLY=( $(compgen -f -- ${cur}) )
}
complete -F _media_manager_completion media-manager
