workspace "Предиктор Риска" "Система прогнозирования осложнений после CABG" {

    !identifiers hierarchical

    model {

        clinician = person "Врач" "Использует калькулятор риска"

        riskPredictor = softwareSystem "Система прогнозирования риска" "Предсказывает вероятность осложнений после операции АКШ" {

            nginx = container "Reverse Proxy" "Nginx" "Маршрутизирует HTTP-запросы и раздает фронтенд"

            frontend = container "Фронтенд" "React + TypeScript + Tailwind + shadcn" "Веб-приложение"

            backend = container "Backend API" "FastAPI (Python)" "REST API для предсказаний" {

                api = component "Prediction API" "FastAPI endpoint" "Принимает запросы на прогноз"

                service = component "Risk Prediction Service" "Python service" "Подготавливает признаки и вызывает ML модель"

                mlModel = component "ML модель" "Scikit-learn / XGBoost" "Предсказывает вероятность осложнения"

                repository = component "Prediction Repository" "Data access layer" "Сохраняет результаты прогнозов"

                api -> service "Передает данные пациента"
                service -> mlModel "Выполняет инференс"
                service -> repository "Сохраняет результат"
            }

            database = container "База данных" "PostgreSQL" "Хранит пациентов и результаты прогнозов"
        }

        clinician -> riskPredictor.nginx "Открывает систему в браузере"

        riskPredictor.nginx -> riskPredictor.frontend "Отдает статические файлы"
        riskPredictor.nginx -> riskPredictor.backend "Проксирует /api запросы"

        riskPredictor.frontend -> riskPredictor.backend "POST /predict"

        riskPredictor.backend.repository -> riskPredictor.database "SQL запросы"
    }

    views {

        systemContext riskPredictor {
            include *
            autolayout lr
        }

        container riskPredictor {
            include *
            autolayout lr
        }

        component riskPredictor.backend {
            include *
            autolayout lr
        }

        theme default
    }
}