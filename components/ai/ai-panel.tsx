"use client"

import { useState } from "react"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Send, Bot } from "lucide-react"

export function AIPanel() {
  const [open, setOpen] = useState(false)
  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="outline" className="w-full"><Bot className="mr-2 h-4 w-4" />AI</Button>
      </SheetTrigger>
      <SheetContent side="right" className="w-full max-w-md">
        <SheetHeader><SheetTitle>AI-ассистент</SheetTitle></SheetHeader>
        <div className="mt-4 flex h-[80vh] flex-col">
          <div className="flex-1 overflow-auto rounded-md border p-3 text-sm text-muted-foreground">
            Подсказки и ответы AI…
          </div>
          <div className="mt-3 flex gap-2">
            <Textarea placeholder="Задайте вопрос..." />
            <Button><Send className="h-4 w-4" /></Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
