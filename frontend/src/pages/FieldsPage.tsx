import React, { useEffect, useState } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { getFields, createConfig } from "../services/api";
import { Field } from "../types";

const FieldsPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const { containerSelector, domain } = (location.state as any) || {};

  const [fields, setFields] = useState<Field[]>([]);
  const [selectedFields, setSelectedFields] = useState<Set<string>>(new Set());
  const [fieldNames, setFieldNames] = useState<Record<string, string>>({});
  const [fieldSelectors, setFieldSelectors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFields = async () => {
      try {
        const response = await getFields(sessionId!);
        setFields(response.data.fields);
        // По умолчанию выбираем все поля
        const allSelectors = response.data.fields.map((f) => f.selector);
        setSelectedFields(new Set(allSelectors));
        // Инициализируем имена и селекторы
        const names: Record<string, string> = {};
        const selectors: Record<string, string> = {};
        response.data.fields.forEach((f) => {
          names[f.selector] = f.name;
          selectors[f.selector] = f.selector;
        });
        setFieldNames(names);
        setFieldSelectors(selectors);
      } catch (err) {
        console.error(err);
        setError("Не удалось загрузить поля");
      }
    };
    fetchFields();
  }, [sessionId]);

  const toggleField = (selector: string) => {
    const newSet = new Set(selectedFields);
    if (newSet.has(selector)) {
      newSet.delete(selector);
    } else {
      newSet.add(selector);
    }
    setSelectedFields(newSet);
  };

  const updateFieldName = (selector: string, name: string) => {
    setFieldNames((prev) => ({ ...prev, [selector]: name }));
  };

  const updateFieldSelector = (selector: string, newSelector: string) => {
    setFieldSelectors((prev) => ({ ...prev, [selector]: newSelector }));
  };

  const handleSaveConfig = async () => {
    if (!containerSelector || !domain) {
      alert("Отсутствуют данные о контейнере или домене");
      return;
    }
    setLoading(true);
    try {
      const selected = fields.filter((f) => selectedFields.has(f.selector));
      const fieldsToSave = selected.map((f) => ({
        name: fieldNames[f.selector] || f.name,
        selector: fieldSelectors[f.selector] || f.selector,
        type: f.type,
        attribute: f.attribute,
      }));

      const configData = {
        domain,
        config: {
          container_selector: containerSelector,
          fields: fieldsToSave,
        },
      };

      await createConfig(configData);
      navigate("/configs");
    } catch (err) {
      console.error(err);
      alert("Ошибка при сохранении конфигурации");
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

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          Выберите поля для извлечения
        </h1>

        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {fields.map((field) => (
              <li key={field.selector} className="px-6 py-4">
                <div className="flex items-start">
                  <input
                    type="checkbox"
                    checked={selectedFields.has(field.selector)}
                    onChange={() => toggleField(field.selector)}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded mt-1"
                  />
                  <div className="ml-3 flex-1">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Имя поля
                        </label>
                        <input
                          type="text"
                          value={fieldNames[field.selector] || field.name}
                          onChange={(e) =>
                            updateFieldName(field.selector, e.target.value)
                          }
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          CSS-селектор
                        </label>
                        <input
                          type="text"
                          value={fieldSelectors[field.selector] || field.selector}
                          onChange={(e) =>
                            updateFieldSelector(field.selector, e.target.value)
                          }
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Тип
                        </label>
                        <select
                          disabled
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 bg-gray-50 sm:text-sm"
                        >
                          <option>{field.type}</option>
                        </select>
                      </div>
                    </div>
                    {field.example && (
                      <p className="mt-2 text-sm text-gray-500">
                        Пример: {field.example}
                      </p>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="mt-8 flex justify-end space-x-4">
          <button
            onClick={() => navigate(-1)}
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          >
            Назад
          </button>
          <button
            onClick={handleSaveConfig}
            disabled={loading}
            className="px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? "Сохранение..." : "Сохранить конфигурацию"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default FieldsPage;