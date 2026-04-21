"use client";

import { Expense, CATEGORIES } from "@/lib/storage";

interface Props {
  date: string;
  expenses: Expense[];
  onAdd: () => void;
  onEdit: (expense: Expense) => void;
  onClose: () => void;
}

function formatAmount(n: number): string {
  return n.toLocaleString("ko-KR");
}

export default function DayDetailModal({
  date,
  expenses,
  onAdd,
  onEdit,
  onClose,
}: Props) {
  const [y, m, d] = date.split("-");
  const title = `${y}년 ${Number(m)}월 ${Number(d)}일`;
  const total = expenses.reduce((sum, e) => sum + e.amount, 0);

  return (
    <div
      className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-xl w-full max-w-sm overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-5 pb-3">
          <h3 className="text-lg font-semibold">{title}</h3>
          <p className="text-sm text-gray-400 mt-0.5">{expenses.length}건 · ₩{formatAmount(total)}</p>
        </div>

        {expenses.length > 0 ? (
          <div className="max-h-64 overflow-y-auto divide-y divide-gray-100">
            {expenses.map((exp) => {
              const isInstallment = exp.id.includes("_inst_");
              return (
                <button
                  key={exp.id}
                  onClick={() => onEdit(exp)}
                  className="w-full flex items-center justify-between px-5 py-3 hover:bg-gray-50 transition-colors text-left"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    {exp.category && (
                      <span className="text-base shrink-0">
                        {CATEGORIES.find((c) => c.id === exp.category)?.emoji ?? "📦"}
                      </span>
                    )}
                    <span className="text-sm text-gray-700 truncate">{exp.item}</span>
                    {isInstallment && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-600 shrink-0">
                        할부
                      </span>
                    )}
                  </div>
                  <span className={`text-sm font-medium shrink-0 ml-3 ${isInstallment ? "text-amber-600" : "text-blue-600"}`}>
                    ₩{formatAmount(exp.amount)}
                  </span>
                </button>
              );
            })}
          </div>
        ) : (
          <div className="px-5 py-6 text-center text-sm text-gray-400">
            지출 내역이 없습니다
          </div>
        )}

        <div className="p-4 border-t border-gray-100 flex gap-2">
          <button
            onClick={onAdd}
            className="flex-1 bg-blue-600 text-white py-2.5 rounded-xl text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            + 추가
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2.5 bg-gray-100 text-gray-600 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
}
