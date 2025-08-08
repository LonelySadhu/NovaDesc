import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function DashboardPage() {
  return (
    <div className="container py-6 space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <Kpi title="Активные заявки" value="24" />
        <Kpi title="Просрочено" value="5" />
        <Kpi title="На неделю" value="31" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <Card><CardHeader><CardTitle>Выполненные работы</CardTitle></CardHeader><CardContent>/* chart */</CardContent></Card>
        <Card><CardHeader><CardTitle>Частота поломок</CardTitle></CardHeader><CardContent>/* chart */</CardContent></Card>
      </div>
    </div>
  )
}

function Kpi({ title, value }: { title: string; value: string }) {
  return (
    <Card>
      <CardHeader><CardTitle className="text-sm text-muted-foreground">{title}</CardTitle></CardHeader>
      <CardContent><div className="text-3xl font-semibold">{value}</div></CardContent>
    </Card>
  )
}
