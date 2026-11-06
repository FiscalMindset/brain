# Authorization
`require_user` on every user route; queries always filter `user_id`; memory/graph/project/source detail return 404 for other users' rows (never 403-with-data).
