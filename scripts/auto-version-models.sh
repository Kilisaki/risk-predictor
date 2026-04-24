#!/bin/bash
# scripts/auto-version-models.sh
# Автоматическое версионирование моделей при пуше

set -e

MODELS_DIR="ml_service/model_versions"
cd "$(git rev-parse --show-toplevel)"  # переходим в корень репозитория

# Находим максимальную версию
MAX_VER=$(ls "$MODELS_DIR"/model_v*.pkl 2>/dev/null | 
          sed 's/.*model_v\([0-9]*\)\.pkl/\1/' | 
          sort -n | 
          tail -1)

if [ -z "$MAX_VER" ]; then
    NEXT_VER=1
else
    NEXT_VER=$((MAX_VER + 1))
fi

# Ищем неподписанные файлы .pkl (без model_vX)
for file in "$MODELS_DIR"/*.pkl; do
    filename=$(basename "$file")
    if [[ ! "$filename" =~ ^model_v[0-9]+\.pkl$ ]]; then
        new_name="model_v${NEXT_VER}.pkl"
        echo "📦 Auto-versioning: $filename → $new_name"
        mv "$file" "$MODELS_DIR/$new_name"
        
        # Обновляем latest.pkl (симлинк)
        ln -sf "$new_name" "$MODELS_DIR/latest.pkl"
        
        # Добавляем в git
        git add "$MODELS_DIR/$new_name"
        git rm --cached "$file" 2>/dev/null || true
        rm -f "$file" 2>/dev/null || true
        
        NEXT_VER=$((NEXT_VER + 1))
    fi
done

# Если есть latest.pkl - обновляем ссылку на последнюю версию
LATEST_MODEL=$(ls "$MODELS_DIR"/model_v*.pkl 2>/dev/null | sort -V | tail -1)
if [ -n "$LATEST_MODEL" ]; then
    ln -sf "$(basename "$LATEST_MODEL")" "$MODELS_DIR/latest.pkl"
    git add "$MODELS_DIR/latest.pkl"
fi

echo "✅ Done. Latest model: $(basename "$LATEST_MODEL")"
