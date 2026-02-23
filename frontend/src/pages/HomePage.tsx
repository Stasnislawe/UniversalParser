import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { startAnalysis } from "../services/api";

const HomePage: React.FC = () => {
  const [url, setUrl] = useState("");
  const [useJs, setUseJs] = useState(true);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await startAnalysis(url, useJs);
      navigate(`/analysis/${response.data.task_id}`, { state: { url } });
    } catch (error) {
      console.error("Failed to start analysis:", error);
      alert("Ошибка при запуске анализа");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Универсальный парсер
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Введите URL страницы для анализа
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label
                htmlFor="url"
                className="block text-sm font-medium text-gray-700"
              >
                URL
              </label>
              <div className="mt-1">
                <input
                  id="url"
                  name="url"
                  type="url"
                  required
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  placeholder="https://example.com"
                />
              </div>
            </div>

            <div className="flex items-center">
              <input
                id="useJs"
                name="useJs"
                type="checkbox"
                checked={useJs}
                onChange={(e) => setUseJs(e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label
                htmlFor="useJs"
                className="ml-2 block text-sm text-gray-900"
              >
                Загружать с JavaScript (для динамических сайтов)
              </label>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                {loading ? "Загрузка..." : "Анализировать"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default HomePage;