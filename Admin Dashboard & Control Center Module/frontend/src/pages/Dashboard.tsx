import { Users, Calendar, FileText, Activity } from "lucide-react";
import { KPICard } from "@/components/dashboard/KPICard";
import { QuickActions } from "@/components/dashboard/QuickActions";
import { StatusCard } from "@/components/dashboard/StatusCard";
import { motion } from "framer-motion";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const appointmentData = [
  { name: "Mon", appointments: 65 },
  { name: "Tue", appointments: 78 },
  { name: "Wed", appointments: 90 },
  { name: "Thu", appointments: 81 },
  { name: "Fri", appointments: 95 },
  { name: "Sat", appointments: 55 },
  { name: "Sun", appointments: 40 },
];

const revenueData = [
  { name: "Jan", revenue: 4000 },
  { name: "Feb", revenue: 3000 },
  { name: "Mar", revenue: 5000 },
  { name: "Apr", revenue: 4500 },
  { name: "May", revenue: 6000 },
  { name: "Jun", revenue: 5500 },
];

export default function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl bg-gradient-hero p-8 text-white shadow-large"
      >
        <h1 className="text-3xl font-bold mb-2">Welcome back, Admin! 👋</h1>
        <p className="text-white/90">Here's what's happening with your clinic today.</p>
      </motion.div>

      {/* KPI Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <KPICard
          title="Total Patients"
          value={2847}
          icon={Users}
          trend={{ value: 12.5, isPositive: true }}
          delay={0.1}
        />
        <KPICard
          title="Active Appointments"
          value={142}
          icon={Calendar}
          trend={{ value: 8.2, isPositive: true }}
          delay={0.2}
        />
        <KPICard
          title="Pending Invoices"
          value={23}
          icon={FileText}
          trend={{ value: 3.1, isPositive: false }}
          delay={0.3}
        />
        <KPICard title="System Health" value={98} icon={Activity} delay={0.4} />
      </div>

      {/* Quick Actions */}
      <QuickActions />

      {/* Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardHeader>
              <CardTitle>Weekly Appointments</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={appointmentData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" />
                  <YAxis stroke="hsl(var(--muted-foreground))" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="appointments"
                    stroke="hsl(var(--primary))"
                    strokeWidth={2}
                    dot={{ fill: "hsl(var(--primary))", r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.6 }}>
          <Card>
            <CardHeader>
              <CardTitle>Monthly Revenue</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={revenueData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" />
                  <YAxis stroke="hsl(var(--muted-foreground))" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                    }}
                  />
                  <Bar dataKey="revenue" fill="hsl(var(--accent))" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* System Status */}
      <div>
        <h2 className="text-2xl font-bold mb-4">System Monitoring</h2>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <StatusCard
            title="Patient Module"
            status="online"
            icon={Users}
            metrics={[
              { label: "Uptime", value: "99.9%" },
              { label: "Response", value: "45ms" },
            ]}
            delay={0.1}
          />
          <StatusCard
            title="Appointments"
            status="online"
            icon={Calendar}
            metrics={[
              { label: "Uptime", value: "99.8%" },
              { label: "Response", value: "52ms" },
            ]}
            delay={0.2}
          />
          <StatusCard
            title="Billing System"
            status="slow"
            icon={FileText}
            metrics={[
              { label: "Uptime", value: "98.5%" },
              { label: "Response", value: "180ms" },
            ]}
            delay={0.3}
          />
        </div>
      </div>
    </div>
  );
}
