.PHONY: upd down logs restart clean migrate revision

upd:
	docker compose up -d
	@echo "\n✅ Tutorial environment is ready!"
	@echo "📖 API docs: http://localhost:8001/docs"
	@echo "🗄️  Adminer: http://localhost:8081 (server: db, user: tutorial, password: tutorial, database: tutorial)"

down:
	docker compose down

logs:
	docker compose logs -f api

restart:
	docker compose restart api

clean:
	docker compose down -v
	@echo "✅ All containers and volumes removed"
