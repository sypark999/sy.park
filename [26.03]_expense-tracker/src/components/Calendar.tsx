"use client";

import { useState, useEffect, useCallback } from "react";
import {
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  eachDayOfInterval,
  format,
  addMonths,
  subMonths,
  isSameMonth,
  isToday,
  startOfWeek as getStartOfWeek,
  endOfWeek as getEndOfWeek,
} from "date-fns";
import { ko } from "date-fns/locale";
import { v4 as uuidv4 } from "uuid";
import {
  Expense,
  CATEGORIES,
  autoCategory,
  loadExpenses,
  saveExpenses,
  addExpense,
  updateExpense,
  deleteExpense,
  expandInstallments,
  getExpensesByDateRange,
  sumExpenses,
} from "@/lib/storage";
import ExpenseModal from "./ExpenseModal";
import DayDetailModal from "./DayDetailModal";
import { seedData } from "@/lib/seed";

type PeriodMode = "month" | "week" | "custom";

function formatAmount(n: number): string {
  return n.toLocaleString("ko-KR");
}

export default function Calendar() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [modalDate, setModalDate] = useState<string | null>(null);
  const [detailDate, setDetailDate] = useState<string | null>(null);
  const [editingExpense, setEditingExpense] = useState<Expense | null>(null);
  const [periodMode, setPeriodMode] = useState<PeriodMode>("month");
  const [customStart, setCustomStart] = useState("");
  const [customEnd, setCustomEnd] = useState("");
  const [excludeInstallment, setExcludeInstallment] = useState(false);

  useEffect(() => {
    // 시드 데이터 버전 관리 - 버전이 다르면 재초기화
    const SEED_VERSION = "2";
    const currentVersion = localStorage.getItem("expense-tracker-seed-version");
    if (currentVersion !== SEED_VERSION) {
      localStorage.removeItem("expense-tracker-data");
      localStorage.setItem("expense-tracker-seed-version", SEED_VERSION);
    }

    loadExpenses().then((data) => {
      if (data.length === 0) {
        saveExpenses(seedData).then(setExpenses);
      } else {
        // 카테고리 없는 기존 데이터 자동 분류
        const needsMigration = data.some((e) => !e.category);
        if (needsMigration) {
          const migrated = data.map((e) =>
            e.category ? e : { ...e, category: autoCategory(e.item) }
          );
          saveExpenses(migrated).then(setExpenses);
        } else {
          setExpenses(data);
        }
      }
    });
  }, []);

  // 할부를 월별로 펼친 가상 목록 (캘린더 표시 + 합산용)
  const expandedExpenses = expandInstallments(expenses);

  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const calendarStart = startOfWeek(monthStart, { weekStartsOn: 0 });
  const calendarEnd = endOfWeek(monthEnd, { weekStartsOn: 0 });
  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd });

  const dayLabels = ["일", "월", "화", "수", "목", "금", "토"];

  const getExpensesForDate = useCallback(
    (date: Date) => {
      const key = format(date, "yyyy-MM-dd");
      return expandedExpenses.filter((e) => e.date === key);
    },
    [expandedExpenses]
  );

  const getSummaryRange = (): { start: string; end: string; label: string } => {
    if (periodMode === "month") {
      return {
        start: format(monthStart, "yyyy-MM-dd"),
        end: format(monthEnd, "yyyy-MM-dd"),
        label: format(currentDate, "yyyy년 M월"),
      };
    }
    if (periodMode === "week") {
      const ws = getStartOfWeek(new Date(), { weekStartsOn: 0 });
      const we = getEndOfWeek(new Date(), { weekStartsOn: 0 });
      return {
        start: format(ws, "yyyy-MM-dd"),
        end: format(we, "yyyy-MM-dd"),
        label: `이번 주 (${format(ws, "M/d")}~${format(we, "M/d")})`,
      };
    }
    return {
      start: customStart || format(monthStart, "yyyy-MM-dd"),
      end: customEnd || format(monthEnd, "yyyy-MM-dd"),
      label: customStart && customEnd
        ? `${customStart} ~ ${customEnd}`
        : "기간을 선택하세요",
    };
  };

  const summary = getSummaryRange();
  const periodExpenses = getExpensesByDateRange(expandedExpenses, summary.start, summary.end);
  const periodTotal = sumExpenses(periodExpenses);
  const periodTotalExcluded = sumExpenses(
    periodExpenses.filter((e) => !e.id.includes("_inst_") && !e.installment)
  );

  const handleDayClick = (date: Date) => {
    setDetailDate(format(date, "yyyy-MM-dd"));
  };

  // 할부 가상 항목 클릭 시 원본 expense를 찾아 편집
  const handleExpenseClick = (e: React.MouseEvent, exp: Expense) => {
    e.stopPropagation();
    const originalId = exp.id.includes("_inst_")
      ? exp.id.split("_inst_")[0]
      : exp.id;
    const original = expenses.find((x) => x.id === originalId);
    if (original) {
      setEditingExpense(original);
      setModalDate(original.date);
    }
  };

  const handleSave = async (item: string, amount: number, category: string, installment?: number) => {
    if (editingExpense) {
      const updated = { ...editingExpense, item, amount, category, installment };
      const result = await updateExpense(updated);
      setExpenses(result);
    } else if (modalDate) {
      const newExpense: Expense = {
        id: uuidv4(),
        date: modalDate,
        item,
        amount,
        category,
        installment,
      };
      const result = await addExpense(newExpense);
      setExpenses(result);
    }
    setModalDate(null);
    setEditingExpense(null);
  };

  const handleDelete = async () => {
    if (editingExpense) {
      const result = await deleteExpense(editingExpense.id);
      setExpenses(result);
      setModalDate(null);
      setEditingExpense(null);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-4 sm:p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setCurrentDate(subMonths(currentDate, 1))}
            className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-gray-100 text-gray-500 transition-colors"
          >
            ◀
          </button>
          <h1 className="text-xl font-bold">
            {format(currentDate, "yyyy년 M월", { locale: ko })}
          </h1>
          <button
            onClick={() => setCurrentDate(addMonths(currentDate, 1))}
            className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-gray-100 text-gray-500 transition-colors"
          >
            ▶
          </button>
        </div>

        {/* Period Toggle */}
        <div className="flex bg-gray-100 rounded-lg p-0.5 text-xs">
          {(["month", "week", "custom"] as PeriodMode[]).map((mode) => (
            <button
              key={mode}
              onClick={() => setPeriodMode(mode)}
              className={`px-3 py-1.5 rounded-md transition-colors ${
                periodMode === mode
                  ? "bg-white shadow text-blue-600 font-medium"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              {mode === "month" ? "월별" : mode === "week" ? "주별" : "기간"}
            </button>
          ))}
        </div>
      </div>

      {/* Custom Period Picker */}
      {periodMode === "custom" && (
        <div className="flex items-center gap-2 mb-4 text-sm">
          <input
            type="date"
            value={customStart}
            onChange={(e) => setCustomStart(e.target.value)}
            className="px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <span className="text-gray-400">~</span>
          <input
            type="date"
            value={customEnd}
            onChange={(e) => setCustomEnd(e.target.value)}
            className="px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      )}

      {/* Day Headers */}
      <div className="grid grid-cols-7 mb-1">
        {dayLabels.map((label, i) => (
          <div
            key={label}
            className={`text-center text-xs font-medium py-2 ${
              i === 0 ? "text-red-400" : i === 6 ? "text-blue-400" : "text-gray-400"
            }`}
          >
            {label}
          </div>
        ))}
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 border-t border-l border-gray-200">
        {days.map((day) => {
          const dayExpenses = getExpensesForDate(day);
          const inMonth = isSameMonth(day, currentDate);
          const today = isToday(day);
          const dayOfWeek = day.getDay();

          return (
            <div
              key={day.toISOString()}
              onClick={() => handleDayClick(day)}
              className={`border-r border-b border-gray-200 min-h-[90px] p-1.5 cursor-pointer transition-colors hover:bg-blue-50/50 ${
                !inMonth ? "bg-gray-50/50" : "bg-white"
              }`}
            >
              <div
                className={`text-xs mb-1 w-6 h-6 flex items-center justify-center rounded-full ${
                  today
                    ? "bg-blue-600 text-white font-bold"
                    : !inMonth
                    ? "text-gray-300"
                    : dayOfWeek === 0
                    ? "text-red-500"
                    : dayOfWeek === 6
                    ? "text-blue-500"
                    : "text-gray-700"
                }`}
              >
                {format(day, "d")}
              </div>

              <div className="space-y-0.5">
                {dayExpenses.slice(0, 3).map((exp) => {
                  const isInstallment = exp.id.includes("_inst_");
                  return (
                    <div
                      key={exp.id}
                      onClick={(e) => handleExpenseClick(e, exp)}
                      className={`text-[10px] leading-tight truncate px-1 py-0.5 rounded transition-colors ${
                        isInstallment
                          ? "bg-amber-50 hover:bg-amber-100"
                          : "bg-blue-50 hover:bg-blue-100"
                      }`}
                    >
                      <span className="text-gray-600">{exp.item}</span>{" "}
                      <span className={`font-medium ${isInstallment ? "text-amber-600" : "text-blue-600"}`}>
                        {formatAmount(exp.amount)}
                      </span>
                    </div>
                  );
                })}
                {dayExpenses.length > 3 && (
                  <div className="text-[10px] text-gray-400 px-1">
                    +{dayExpenses.length - 3}건
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="mt-4 bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500">{summary.label}</p>
            <p className="text-2xl font-bold mt-1">
              ₩{formatAmount(excludeInstallment ? periodTotalExcluded : periodTotal)}
            </p>
            {excludeInstallment && periodTotal !== periodTotalExcluded && (
              <p className="text-xs text-gray-400 mt-1">
                할부 포함 시 ₩{formatAmount(periodTotal)}
              </p>
            )}
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-400 mb-2">
              {periodExpenses.length}건
            </div>
            <button
              onClick={() => setExcludeInstallment(!excludeInstallment)}
              className={`text-xs px-2.5 py-1 rounded-lg transition-colors ${
                excludeInstallment
                  ? "bg-amber-100 text-amber-700"
                  : "bg-gray-100 text-gray-500"
              }`}
            >
              할부 제외 {excludeInstallment ? "ON" : "OFF"}
            </button>
          </div>
        </div>
      </div>

      {/* Category Breakdown */}
      {periodExpenses.length > 0 && (() => {
        const catMap: Record<string, number> = {};
        for (const exp of periodExpenses) {
          const key = exp.category ?? "기타";
          catMap[key] = (catMap[key] ?? 0) + exp.amount;
        }
        const sorted = Object.entries(catMap).sort((a, b) => b[1] - a[1]);
        const maxAmt = sorted[0]?.[1] ?? 1;
        return (
          <div className="mt-3 bg-white rounded-xl border border-gray-200 p-4">
            <p className="text-xs font-medium text-gray-400 mb-3">카테고리별</p>
            <div className="space-y-2.5">
              {sorted.map(([catId, amt]) => {
                const catInfo = CATEGORIES.find((c) => c.id === catId);
                const emoji = catInfo?.emoji ?? "📦";
                const pct = Math.round((amt / periodTotal) * 100);
                const barW = Math.round((amt / maxAmt) * 100);
                return (
                  <div key={catId}>
                    <div className="flex items-center justify-between mb-0.5">
                      <span className="text-xs text-gray-700 flex items-center gap-1">
                        <span>{emoji}</span>
                        <span>{catId}</span>
                      </span>
                      <span className="text-xs text-gray-500">
                        ₩{formatAmount(amt)}
                        <span className="text-gray-300 ml-1">{pct}%</span>
                      </span>
                    </div>
                    <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-400 rounded-full"
                        style={{ width: `${barW}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })()}

      {/* Item List */}
      {periodExpenses.length > 0 && (
        <div className="mt-3 bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
          {periodExpenses
            .sort((a, b) => a.date.localeCompare(b.date))
            .map((exp) => {
              const isInstallment = exp.id.includes("_inst_");
              const [, m, d] = exp.date.split("-");
              return (
                <div
                  key={exp.id}
                  className="flex items-center justify-between px-4 py-2.5"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="text-xs text-gray-400 shrink-0 w-10">
                      {Number(m)}/{Number(d)}
                    </span>
                    <span className="text-sm text-gray-700 truncate">
                      {exp.item}
                    </span>
                    {isInstallment && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-600 shrink-0">
                        할부
                      </span>
                    )}
                  </div>
                  <span
                    className={`text-sm font-medium shrink-0 ml-3 ${
                      isInstallment ? "text-amber-600" : "text-gray-900"
                    }`}
                  >
                    ₩{formatAmount(exp.amount)}
                  </span>
                </div>
              );
            })}
        </div>
      )}

      {/* Day Detail Modal */}
      {detailDate && !modalDate && (
        <DayDetailModal
          date={detailDate}
          expenses={expandedExpenses.filter((e) => e.date === detailDate)}
          onAdd={() => {
            setEditingExpense(null);
            setModalDate(detailDate);
          }}
          onEdit={(exp) => {
            const originalId = exp.id.includes("_inst_")
              ? exp.id.split("_inst_")[0]
              : exp.id;
            const original = expenses.find((x) => x.id === originalId);
            if (original) {
              setEditingExpense(original);
              setModalDate(original.date);
            }
          }}
          onClose={() => setDetailDate(null)}
        />
      )}

      {/* Add/Edit Modal */}
      {modalDate && (
        <ExpenseModal
          date={modalDate}
          expense={editingExpense}
          onSave={handleSave}
          onDelete={editingExpense ? handleDelete : undefined}
          onClose={() => {
            setModalDate(null);
            setEditingExpense(null);
          }}
        />
      )}
    </div>
  );
}
