import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getConfigs } from "../services/api";
import { ParserConfig } from "../types";

const ConfigsPage: React.FC = () => {
  const [configs, setConfigs] = useState<ParserConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchConfigs = async () => {
      try {
        const response = await getConfigs();
        setConfigs(response.data);
      } catch (error) {
        console.error("Failed to fetch configs", error);
      } finally {
        setLoading(false);
      }
    };
    fetchConfigs();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка конфигураций...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Сохранённые конфигурации
          </h1>
          <button
            onClick={() => navigate("/")}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            Новый анализ
          </button>
        </div>

        {configs.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <p className="text-gray-500">Нет сохранённых конфигураций</p>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {configs.map((config) => (
              <div
                key={config.id}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition"
              >
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  {config.domain}
                </h2>
                <p className="text-sm text-gray-500 mb-4">
                  Создано: {new Date(config.created_at).toLocaleString()}
                </p>
                <p className="text-sm text-gray-700 mb-4">
                  Селектор контейнера:{" "}
                  <code className="bg-gray-100 px-1">
                    {config.config.container_selector}
                  </code>
                </p>
                <p className="text-sm text-gray-700 mb-4">
                  Полей: {config.config.fields.length}
                </p>
                <div className="flex justify-end space-x-2">
                  <Link
                    to={`/scrape/${config.id}`}
                    className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                  >
                    Запустить сбор
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ConfigsPage;