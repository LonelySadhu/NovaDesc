import { RequestsList } from "@/components/requests/requests-list"

const data = [
  { id: "1", title: "Замена фильтра", equipment: "Компрессор-12", priority: "high", status: "new", dueDate: "12.09" },
  { id: "2", title: "Диагностика вибрации", equipment: "Насос-7", priority: "medium", status: "in_progress", dueDate: "10.09" },
] as any

export default function RequestsPage() {
  return <div className="container py-6"><RequestsList data={data} /></div>
}
