# Docker aliases
alias d='docker'
alias dc='docker compose'
alias dps='docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
alias dpsa='docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
alias dlog='docker logs -f'
alias dex='docker exec -it'
alias dprune='docker system prune -af && docker volume prune -f'
alias dstats='docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"'

# Docker compose shortcuts
alias dcup='docker compose up -d'
alias dcdown='docker compose down'
alias dcrestart='docker compose restart'
alias dcpull='docker compose pull'
alias dcbuild='docker compose build --no-cache'
alias dclogs='docker compose logs -f'

# Navigation
alias apps='cd ~/apps'
alias traefik='cd ~/traefik'
alias envs='cd ~/envs'

# System
alias ports='sudo netstat -tlnp'
alias mem='free -h'
alias disk='df -h'
alias cpu='htop'

# Logs
alias syslog='sudo tail -f /var/log/syslog'
alias authlog='sudo tail -f /var/log/auth.log'

# Quick edits
alias hosts='sudo nano /etc/hosts'
alias bashrc='nano ~/.bashrc && source ~/.bashrc'

# Safety
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

# Git
alias gs='git status'
alias gp='git pull'
alias gl='git log --oneline -10'
