import React, { useEffect, useState } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { getAnalysisStatus, getCandidates, selectContainer } from "../services/api";
import { Candidate } from "../types";

const AnalysisPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const [status, setStatus] = useState<string>("PENDING");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<number | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const location = useLocation();
  const { url } = (location.state as { url?: string }) || {};


  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const statusRes = await getAnalysisStatus(taskId!);
        setStatus(statusRes.data.status);

        if (statusRes.data.status === "SUCCESS" && statusRes.data.session_id) {
          setSessionId(statusRes.data.session_id);
          // Загружаем кандидатов
          const candidatesRes = await getCandidates(statusRes.data.session_id);
          setCandidates(candidatesRes.data.candidates);
          clearInterval(interval);
        } else if (statusRes.data.status === "FAILURE") {
          setError(statusRes.data.error || "Анализ не удался");
          clearInterval(interval);
        }
      } catch (err) {
        console.error(err);
        setError("Ошибка при проверке статуса");
        clearInterval(interval);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [taskId]);

  const handleSelectCandidate = async () => {
    if (!sessionId || selectedCandidate === null || !url) return;
    setLoading(true);
    try {
      const candidate = candidates.find((c) => c.id === selectedCandidate);
      if (!candidate) return;
      await selectContainer(sessionId, candidate.container_selector);
      const domain = new URL(url).hostname;
      navigate(`/fields/${sessionId}`, {
        state: {
          containerSelector: candidate.container_selector,
          domain,
        },
      });
    } catch (err) {
      console.error(err);
      alert("Ошибка при выборе контейнера");
    } finally {
      setLoading(false);
    }
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded shadow-md">
          <h2 className="text-xl font-bold text-red-600">Ошибка</h2>
          <p className="mt-2">{error}</p>
          <button
            onClick={() => navigate("/")}
            className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded"
          >
            На главную
          </button>
        </div>
      </div>
    );
  }

  if (status === "PENDING") {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Анализ страницы...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          Выберите блок с данными
        </h1>
        <p className="text-gray-600 mb-8">
          Найдено {candidates.length} кандидатов на повторяющиеся блоки. Выберите тот, который содержит нужные элементы.
        </p>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {candidates.map((candidate) => (
            <div
              key={candidate.id}
              className={`bg-white rounded-lg shadow-md p-6 border-2 cursor-pointer transition ${
                selectedCandidate === candidate.id
                  ? "border-indigo-500"
                  : "border-transparent hover:border-gray-300"
              }`}
              onClick={() => setSelectedCandidate(candidate.id)}
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Вариант {candidate.id}
              </h3>
              <p className="text-sm text-gray-500 mb-2">
                Селектор: <code className="bg-gray-100 px-1">{candidate.container_selector}</code>
              </p>
              <p className="text-sm text-gray-500 mb-4">
                Найдено блоков: {candidate.count}
              </p>
              <div className="border-t pt-4">
                <p className="text-sm font-medium text-gray-700 mb-2">
                  Пример содержимого:
                </p>
                {candidate.example_items.map((html, idx) => (
                  <details key={idx} className="mb-2">
                    <summary className="text-xs text-indigo-600 cursor-pointer">
                      Блок {idx + 1}
                    </summary>
                    <pre className="mt-1 text-xs bg-gray-50 p-2 rounded overflow-auto max-h-32">
                      {html}
                    </pre>
                  </details>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-8 flex justify-end">
          <button
            onClick={handleSelectCandidate}
            disabled={selectedCandidate === null || loading}
            className="px-6 py-3 bg-indigo-600 text-white rounded-md shadow hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? "Обработка..." : "Выбрать этот блок"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AnalysisPage;