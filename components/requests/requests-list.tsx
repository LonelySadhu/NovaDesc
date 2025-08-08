"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTrigger } from "@/components/ui/sheet";
import { Separator } from "@/components/ui/separator";
import { MoreHorizontal, Filter, Plus } from "lucide-react";
import clsx from "clsx";

type Request = {
  id: string;
  title: string;
  equipment: string;
  priority: "low" | "medium" | "high";
  status: "new" | "in_progress" | "done" | "overdue";
  dueDate?: string;
  assignee?: string;
};

export function RequestsList({ data }: { data: Request[] }) {
  const [openFilter, setOpenFilter] = useState(false);

  function Filters() {
    return (
      <div className="flex flex-col gap-4 p-4">
        <div className="text-sm font-medium">Фильтры</div>
        <Button onClick={() => setOpenFilter(false)}>Применить</Button>
      </div>
    );
  }

  function MobileCards() {
    return (
      <div className="space-y-3 md:hidden">
        {data.map((r) => (
          <Card key={r.id}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0">
              <div className="text-base font-medium">{r.title}</div>
              <Badge
                variant="secondary"
                className={clsx(
                  r.status === "overdue" && "bg-red-100 text-red-700",
                  r.status === "in_progress" && "bg-blue-100 text-blue-700",
                  r.status === "done" && "bg-green-100 text-green-700"
                )}
              >
                {mapStatus(r.status)}
              </Badge>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="text-sm text-muted-foreground">{r.equipment}</div>
              <div className="flex items-center gap-2">
                <Badge variant="outline">{mapPriority(r.priority)}</Badge>
                {r.dueDate && <span className="text-xs text-muted-foreground">до {r.dueDate}</span>}
              </div>
            </CardContent>
            <CardFooter className="flex gap-2">
              <Button size="sm" className="flex-1">В работу</Button>
              <Button size="sm" variant="outline" className="flex-1">Закрыть</Button>
              <Button size="icon" variant="ghost"><MoreHorizontal className="h-4 w-4" /></Button>
            </CardFooter>
          </Card>
        ))}

        <div className="fixed inset-x-0 bottom-0 z-10 border-t bg-background/95 p-3 backdrop-blur md:hidden">
          <div className="flex gap-2">
            <Sheet open={openFilter} onOpenChange={setOpenFilter}>
              <SheetTrigger asChild>
                <Button variant="outline" className="flex-1"><Filter className="mr-2 h-4 w-4" />Фильтры</Button>
              </SheetTrigger>
              <SheetContent side="bottom" className="h-[75vh]">
                <SheetHeader>Фильтры</SheetHeader>
                <Separator className="my-2" />
                <Filters />
              </SheetContent>
            </Sheet>
            <Button className="flex-1"><Plus className="mr-2 h-4 w-4" />Новая заявка</Button>
          </div>
        </div>
      </div>
    );
  }

  function DesktopTable() {
    return (
      <div className="hidden md:block">
        <div className="mb-3 flex items-center gap-2">
          <Button variant="outline" onClick={() => setOpenFilter(true)}><Filter className="mr-2 h-4 w-4" />Фильтры</Button>
          <Button><Plus className="mr-2 h-4 w-4" />Новая заявка</Button>
        </div>
        <div className="w-full overflow-x-auto rounded-md border">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="p-3 text-left">Заявка</th>
                <th className="p-3 text-left">Оборудование</th>
                <th className="p-3 text-left">Приоритет</th>
                <th className="p-3 text-left">Статус</th>
                <th className="p-3 text-left">Дедлайн</th>
                <th className="p-3 text-left">Действия</th>
              </tr>
            </thead>
            <tbody>
              {data.map((r) => (
                <tr key={r.id} className="border-t">
                  <td className="p-3">{r.title}</td>
                  <td className="p-3">{r.equipment}</td>
                  <td className="p-3">{mapPriority(r.priority)}</td>
                  <td className="p-3">{mapStatus(r.status)}</td>
                  <td className="p-3">{r.dueDate ?? "—"}</td>
                  <td className="p-3">
                    <div className="flex gap-2">
                      <Button size="sm">В работу</Button>
                      <Button size="sm" variant="outline">Закрыть</Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <Sheet open={openFilter} onOpenChange={setOpenFilter}>
          <SheetContent side="right" className="w-[380px]">
            <SheetHeader>Фильтры</SheetHeader>
            <Separator className="my-2" />
            <Filters />
          </SheetContent>
        </Sheet>
      </div>
    );
  }

  return (
    <>
      <MobileCards />
      <DesktopTable />
    </>
  );
}

function mapPriority(p: Request["priority"]) {
  return p === "high" ? "Высокий" : p === "medium" ? "Средний" : "Низкий";
}
function mapStatus(s: Request["status"]) {
  switch (s) {
    case "new": return "Новая";
    case "in_progress": return "В работе";
    case "done": return "Выполнена";
    case "overdue": return "Просрочена";
  }
}
