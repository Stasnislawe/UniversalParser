import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getConfig, startScrape, getScrapeStatus } from "../services/api";
import { ParserConfig } from "../types";

const ScrapePage: React.FC = () => {
  const { configId } = useParams<{ configId: string }>();
  const navigate = useNavigate();
  const [config, setConfig] = useState<ParserConfig | null>(null);
  const [startUrl, setStartUrl] = useState("");
  const [maxPages, setMaxPages] = useState<number | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [pagesProcessed, setPagesProcessed] = useState(0);
  const [itemsCount, setItemsCount] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await getConfig(Number(configId));
        setConfig(response.data);
        // Предзаполняем URL из шаблона, если есть
        if (response.data.url_pattern) {
          setStartUrl(response.data.url_pattern.replace("{page}", "1"));
        }
      } catch (err) {
        console.error(err);
        setError("Не удалось загрузить конфигурацию");
      }
    };
    if (configId) fetchConfig();
  }, [configId]);

  const handleStart = async () => {
    if (!config) return;
    setLoading(true);
    setTaskId(null);
    setStatus(null);
    setError(null);
    try {
      const response = await startScrape(config.id, startUrl, maxPages);
      setTaskId(response.data.task_id);
      // Начинаем опрос статуса
      pollStatus(response.data.task_id);
    } catch (err) {
      console.error(err);
      setError("Ошибка при запуске сбора");
      setLoading(false);
    }
  };

  const pollStatus = async (id: string) => {
    const interval = setInterval(async () => {
      try {
        const statusRes = await getScrapeStatus(id);
        setStatus(statusRes.data.status);
        setPagesProcessed(statusRes.data.pages_processed || 0);
        setItemsCount(statusRes.data.items_count || 0);
        if (
          statusRes.data.status === "SUCCESS" ||
          statusRes.data.status === "FAILURE"
        ) {
          clearInterval(interval);
          setLoading(false);
          if (statusRes.data.status === "SUCCESS") {
            // Переходим на страницу результатов
            navigate(`/results/${id}`);
          } else {
            setError(statusRes.data.error || "Сбор не удался");
          }
        }
      } catch (err) {
        console.error(err);
        clearInterval(interval);
        setLoading(false);
        setError("Ошибка при проверке статуса");
      }
    }, 2000);
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded shadow-md">
          <h2 className="text-xl font-bold text-red-600">Ошибка</h2>
          <p className="mt-2">{error}</p>
          <button
            onClick={() => navigate("/configs")}
            className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded"
          >
            К списку конфигураций
          </button>
        </div>
      </div>
    );
  }

  if (!config) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка конфигурации...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          Запуск сбора данных
        </h1>

        <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Конфигурация для {config.domain}
            </h3>
          </div>
          <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
            <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-gray-500">
                  Селектор контейнера
                </dt>
                <dd className="mt-1 text-sm text-gray-900">
                  <code className="bg-gray-100 px-1">
                    {config.config.container_selector}
                  </code>
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Полей</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {config.config.fields.length}
                </dd>
              </div>
              {config.config.pagination && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">
                    Тип пагинации
                  </dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {config.config.pagination.type}
                  </dd>
                </div>
              )}
            </dl>
          </div>
        </div>

        <div className="bg-white shadow sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Параметры сбора
            </h3>
            <div className="space-y-4">
              <div>
                <label
                  htmlFor="startUrl"
                  className="block text-sm font-medium text-gray-700"
                >
                  Стартовый URL
                </label>
                <input
                  type="url"
                  name="startUrl"
                  id="startUrl"
                  required
                  value={startUrl}
                  onChange={(e) => setStartUrl(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                />
              </div>
              <div>
                <label
                  htmlFor="maxPages"
                  className="block text-sm font-medium text-gray-700"
                >
                  Максимальное количество страций (оставьте пустым для всех)
                </label>
                <input
                  type="number"
                  name="maxPages"
                  id="maxPages"
                  min="1"
                  value={maxPages || ""}
                  onChange={(e) =>
                    setMaxPages(
                      e.target.value ? parseInt(e.target.value) : undefined
                    )
                  }
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                />
              </div>
            </div>
          </div>
          <div className="px-4 py-3 bg-gray-50 text-right sm:px-6">
            <button
              onClick={handleStart}
              disabled={loading || !startUrl}
              className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? "Запуск..." : "Запустить сбор"}
            </button>
          </div>
        </div>

        {status && (
          <div className="mt-6 bg-white shadow sm:rounded-lg p-4">
            <p className="text-sm text-gray-700">Статус: {status}</p>
            {pagesProcessed > 0 && (
              <p className="text-sm text-gray-700">
                Обработано страниц: {pagesProcessed}
              </p>
            )}
            {itemsCount > 0 && (
              <p className="text-sm text-gray-700">
                Собрано элементов: {itemsCount}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ScrapePage;