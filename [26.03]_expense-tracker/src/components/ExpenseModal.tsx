"use client";

import { useState, useEffect, useRef } from "react";
import { Expense, CATEGORIES } from "@/lib/storage";

interface Props {
  date: string;
  expense?: Expense | null;
  onSave: (item: string, amount: number, category: string, installment?: number) => void;
  onDelete?: () => void;
  onClose: () => void;
}

export default function ExpenseModal({
  date,
  expense,
  onSave,
  onDelete,
  onClose,
}: Props) {
  const [item, setItem] = useState(expense?.item ?? "");
  const [amount, setAmount] = useState(expense?.amount?.toString() ?? "");
  const [category, setCategory] = useState(expense?.category ?? "기타");
  const [useInstallment, setUseInstallment] = useState(
    (expense?.installment ?? 1) > 1
  );
  const [installment, setInstallment] = useState(
    expense?.installment?.toString() ?? "3"
  );
  const itemRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    itemRef.current?.focus();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!item.trim() || !amount.trim()) return;
    const inst = useInstallment ? Number(installment) : undefined;
    onSave(item.trim(), Number(amount), category, inst);
  };

  const formatDate = (d: string) => {
    const [y, m, day] = d.split("-");
    return `${y}년 ${Number(m)}월 ${Number(day)}일`;
  };

  const amountNum = Number(amount) || 0;
  const instNum = Number(installment) || 1;
  const perMonth = useInstallment && instNum > 1 ? Math.round(amountNum / instNum) : 0;

  return (
    <div
      className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="text-lg font-semibold mb-1">{formatDate(date)}</h3>
        <p className="text-sm text-gray-400 mb-4">
          {expense ? "수정" : "새 지출 추가"}
        </p>

        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            ref={itemRef}
            type="text"
            placeholder="항목 (예: 점심, 커피)"
            value={item}
            onChange={(e) => setItem(e.target.value)}
            className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <input
            type="number"
            placeholder="금액"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />

          {/* 카테고리 선택 */}
          <div>
            <p className="text-xs text-gray-400 mb-1.5">카테고리</p>
            <div className="flex flex-wrap gap-1.5">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat.id}
                  type="button"
                  onClick={() => setCategory(cat.id)}
                  className={`px-2.5 py-1 rounded-lg text-xs flex items-center gap-1 transition-colors ${
                    category === cat.id
                      ? "bg-blue-600 text-white font-medium"
                      : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                  }`}
                >
                  <span>{cat.emoji}</span>
                  <span>{cat.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* 할부 옵션 */}
          <div className="border border-gray-200 rounded-xl p-3">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={useInstallment}
                onChange={(e) => setUseInstallment(e.target.checked)}
                className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">할부</span>
            </label>

            {useInstallment && (
              <div className="mt-3 space-y-2">
                <div className="flex items-center gap-2">
                  <select
                    value={installment}
                    onChange={(e) => setInstallment(e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 24].map((n) => (
                      <option key={n} value={n}>
                        {n}개월
                      </option>
                    ))}
                  </select>
                </div>
                {amountNum > 0 && instNum > 1 && (
                  <p className="text-xs text-gray-500">
                    월 <span className="font-medium text-blue-600">₩{perMonth.toLocaleString("ko-KR")}</span> × {instNum}개월
                  </p>
                )}
              </div>
            )}
          </div>

          <div className="flex gap-2 pt-2">
            <button
              type="submit"
              className="flex-1 bg-blue-600 text-white py-3 rounded-xl text-sm font-medium hover:bg-blue-700 transition-colors"
            >
              {expense ? "수정" : "추가"}
            </button>
            {expense && onDelete && (
              <button
                type="button"
                onClick={onDelete}
                className="px-4 py-3 bg-red-50 text-red-600 rounded-xl text-sm font-medium hover:bg-red-100 transition-colors"
              >
                삭제
              </button>
            )}
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-3 bg-gray-100 text-gray-600 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors"
            >
              취소
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
