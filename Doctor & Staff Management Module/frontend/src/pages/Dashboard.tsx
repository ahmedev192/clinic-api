import { motion } from 'framer-motion';
import { Users, Stethoscope, UserCheck, Activity } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { KPICard } from '@/components/dashboard/KPICard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';

const mockStaffData = [
  { month: 'Jan', staff: 24, doctors: 8 },
  { month: 'Feb', staff: 26, doctors: 9 },
  { month: 'Mar', staff: 28, doctors: 10 },
  { month: 'Apr', staff: 30, doctors: 11 },
  { month: 'May', staff: 32, doctors: 12 },
  { month: 'Jun', staff: 35, doctors: 13 },
];

const mockAvailability = [
  { day: 'Mon', rate: 92 },
  { day: 'Tue', rate: 88 },
  { day: 'Wed', rate: 95 },
  { day: 'Thu', rate: 90 },
  { day: 'Fri', rate: 87 },
  { day: 'Sat', rate: 93 },
  { day: 'Sun', rate: 85 },
];

export default function Dashboard() {
  const { t } = useLanguage();

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl bg-gradient-hero p-8 text-white shadow-large"
      >
        <h1 className="text-3xl font-bold mb-2">{t('dashboard')}</h1>
        <p className="text-white/90">Welcome to your Clinic Management System</p>
      </motion.div>

      {/* KPI Cards */}
      <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
        <KPICard
          title={t('total_staff')}
          value={35}
          icon={Users}
          trend={{ value: 12.5, isPositive: true }}
          delay={0.1}
        />
        <KPICard
          title={t('total_doctors')}
          value={13}
          icon={Stethoscope}
          trend={{ value: 8.3, isPositive: true }}
          delay={0.2}
        />
        <KPICard
          title={t('active_staff')}
          value={32}
          icon={UserCheck}
          trend={{ value: 3.2, isPositive: false }}
          delay={0.3}
        />
        <KPICard
          title={t('available_doctors')}
          value={11}
          icon={Activity}
          trend={{ value: 5.1, isPositive: true }}
          delay={0.4}
        />
      </div>

      {/* Charts */}
      <div className="grid gap-6 grid-cols-1 lg:grid-cols-2">
        {/* Staff Growth Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card className="hover:shadow-medium transition-all">
            <CardHeader>
              <CardTitle>Staff & Doctor Growth</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={mockStaffData}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis dataKey="month" className="text-xs" />
                  <YAxis className="text-xs" />
                  <Bar dataKey="staff" fill="hsl(var(--primary))" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="doctors" fill="hsl(var(--accent))" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Availability Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card className="hover:shadow-medium transition-all">
            <CardHeader>
              <CardTitle>Doctor Availability Rate</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={mockAvailability}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis dataKey="day" className="text-xs" />
                  <YAxis className="text-xs" domain={[80, 100]} />
                  <Line 
                    type="monotone" 
                    dataKey="rate" 
                    stroke="hsl(var(--primary))" 
                    strokeWidth={3}
                    dot={{ fill: 'hsl(var(--primary))', r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 grid-cols-1 md:grid-cols-3">
              {[
                { label: 'Add New Staff', icon: Users },
                { label: 'Register Doctor', icon: Stethoscope },
                { label: 'Create Schedule', icon: Activity },
              ].map((action, index) => (
                <motion.button
                  key={action.label}
                  whileHover={{ y: -4, boxShadow: 'var(--shadow-medium)' }}
                  whileTap={{ scale: 0.98 }}
                  className="flex items-center gap-3 p-4 rounded-lg border border-border hover:border-primary/50 transition-all bg-card"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                    <action.icon className="h-5 w-5 text-primary" />
                  </div>
                  <span className="font-medium">{action.label}</span>
                </motion.button>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
