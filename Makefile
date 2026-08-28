# Inspired by: https://blog.mathieu-leplatre.info/tips-for-your-makefile-with-python.html
# 			   https://www.thapaliya.com/en/writings/well-documented-makefiles/

.DEFAULT_GOAL := help

SKILL_DIRS := $(patsubst %/,%,$(wildcard plugins/*/skills/*/))
SKILL_NAMES := $(notdir $(SKILL_DIRS))

help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: install-opencode
install-opencode:  ## Copy skills into ~/.config/opencode/skills/ for OpenCode discovery.
	@for skill in $(SKILL_NAMES); do \
		src="$$(ls -d $(CURDIR)/plugins/*/skills/$$skill 2>/dev/null | head -1)"; \
		dest="$(HOME)/.config/opencode/skills/$$skill"; \
		if [ -n "$$src" ]; then \
			rm -rf "$$dest"; \
			cp -R "$$src" "$$dest"; \
			echo "  copied: $$skill"; \
		else \
			echo "  missing: $$skill"; \
		fi; \
	done

.PHONY: uninstall-opencode
uninstall-opencode:  ## Remove OpenCode skills from ~/.config/opencode/skills/.
	@for skill in $(SKILL_NAMES); do \
		dest="$(HOME)/.config/opencode/skills/$$skill"; \
		if [ -d "$$dest" ]; then \
			rm -rf "$$dest"; \
			echo "  removed: $$skill"; \
		fi; \
	done

.PHONY: install-claude
install-claude:  ## Add marketplace and install all plugins into Claude Code.
	claude plugin marketplace add $(CURDIR) 2>/dev/null || true
	@for plugin in $$(jq -r '.plugins[].name' .claude-plugin/marketplace.json); do \
		echo "  installing: $$plugin"; \
		claude plugin install $$plugin@jh-agent-skills 2>/dev/null || true; \
	done

.PHONY: uninstall-claude
uninstall-claude:  ## Uninstall all plugins and remove marketplace from Claude Code.
	@for plugin in $$(jq -r '.plugins[].name' .claude-plugin/marketplace.json); do \
		claude plugin uninstall $$plugin@jh-agent-skills 2>/dev/null || true; \
		echo "  removed: $$plugin"; \
	done
	claude plugin marketplace remove jh-agent-skills 2>/dev/null || true

.PHONY: validate
validate:  ## Validate all skills and plugin manifests.
	@echo "  validating skills..."
	@for dir in $(SKILL_DIRS); do \
		npx skills-ref validate "$$dir" 2>/dev/null && echo "  ok: $$(basename $$dir)"; \
	done
	@echo "  validating plugins..."
	@for plugin in plugins/*/; do \
		claude plugin validate "$$plugin" 2>/dev/null && echo "  ok: $$(basename $$plugin)"; \
	done

.PHONY: clean
clean:  ## Remove copied skills, caches, and build artifacts.
	@for skill in $(SKILL_NAMES); do \
		dest="$(HOME)/.config/opencode/skills/$$skill"; \
		[ -d "$$dest" ] && rm -rf "$$dest" && echo "  removed: $$skill"; \
	done
	find . -type d -name "__pycache__" | xargs rm -rf 2>/dev/null; true
	rm -rf dist 2>/dev/null; true
