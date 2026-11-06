# Switch integration
1. Install Switch Console (desktop app) and sign in (see https://docs.switchagents.ai/switch-rooms/getting-started).
2. Templates > Import template > paste `secondbrain-room.template.yaml`.
3. Set `bridge` to your messaging app (Slack/Teams/Discord/Mattermost/Telegram) in the room config.
4. Create the room; the first message tags all four agents.
5. Ask `@secondbrain-researcher` a question. Follow the chain: researcher → architect → reviewer → human `approved` → project-manager.

Without Switch: the web UI runs the identical 8-step pipeline via `POST /api/research`.
