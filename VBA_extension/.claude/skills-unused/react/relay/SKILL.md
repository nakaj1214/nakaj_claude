# relay

## Activation
- /relay
- relay

## Usage
- /relay proposal.md
- /relay docs/proposal.md

```bash
set -euo pipefail

ARG="${1:-proposal.md}"

~/.claude/scripts/relay.sh "${ARG}"
