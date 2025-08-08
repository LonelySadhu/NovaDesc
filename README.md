# NovaDesc — Next.js + shadcn/ui Starter (ТОиР SaaS)

Быстрый старт для фронтенда NovaDesc по десктопным макетам с адаптивом под мобильный.

## Старт
1) Создайте проект:
```
npx create-next-app@latest NovaDesc --typescript --eslint --tailwind --app
cd NovaDesc
```
2) UI-зависимости:
```
npx shadcn@latest init
npx shadcn@latest add button card input badge dialog sheet dropdown-menu tabs accordion table toast separator navigation-menu avatar textarea select
npm i @tanstack/react-query zod react-hook-form lucide-react clsx
```
3) Скопируйте файлы из архива поверх вашего проекта.
4) `npm run dev`.

## Что внутри
- Лэйаут: sidebar (desktop) + bottom tab bar (mobile)
- Страницы: dashboard, requests (+ демо списка)
- Компоненты: AI panel, RequestsList (таблица→карточки)
- Токены в `globals.css`, настройки в `tailwind.config.ts`
