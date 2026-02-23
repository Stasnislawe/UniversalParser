import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getScrapeResult, exportResults } from "../services/api";
import { ScrapeResult } from "../types";

const ResultsPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const [result, setResult] = useState<ScrapeResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const response = await getScrapeResult(taskId!);
        setResult(response.data);
      } catch (err) {
        console.error(err);
        setError("Не удалось загрузить результаты");
      } finally {
        setLoading(false);
      }
    };
    fetchResult();
  }, [taskId]);

  const handleExport = (format: "json" | "excel") => {
    const url = exportResults(taskId!, format);
    window.open(url, "_blank");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка результатов...</p>
        </div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded shadow-md">
          <h2 className="text-xl font-bold text-red-600">Ошибка</h2>
          <p className="mt-2">{error || "Результаты не найдены"}</p>
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

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Результаты сбора
          </h1>
          <div className="space-x-2">
            <button
              onClick={() => handleExport("json")}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Скачать JSON
            </button>
            <button
              onClick={() => handleExport("excel")}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Скачать Excel
            </button>
          </div>
        </div>

        <p className="text-gray-600 mb-4">
          Всего собрано элементов: {result.total_items}
        </p>

        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {result.data.length > 0 &&
                    Object.keys(result.data[0]).map((key) => (
                      <th
                        key={key}
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        {key}
                      </th>
                    ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {result.data.slice(0, 10).map((item, idx) => (
                  <tr key={idx}>
                    {Object.values(item).map((value, i) => (
                      <td
                        key={i}
                        className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                      >
                        {value !== null && value !== undefined
                          ? value.toString()
                          : ""}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {result.data.length > 10 && (
            <div className="px-6 py-4 bg-gray-50 text-sm text-gray-500">
              Показаны первые 10 из {result.data.length} записей.
            </div>
          )}
        </div>

        <div className="mt-8 flex justify-end">
          <button
            onClick={() => navigate("/configs")}
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          >
            К списку конфигураций
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;