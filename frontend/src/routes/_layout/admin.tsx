import { createFileRoute, Outlet } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/admin")({
  component: AdminLayout,
  head: () => ({
    meta: [
      {
        title: "Admin - ADTEC",
      },
    ],
  }),
})



function AdminLayout() {
  return <Outlet />
}
