import "./globals.css"
import type { Metadata } from "next"
import ShellLayout from "./(shell)/layout"

export const metadata: Metadata = {
  title: "NovaDesc",
  description: "ТОиР SaaS",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>
        <ShellLayout>{children}</ShellLayout>
      </body>
    </html>
  )
}
