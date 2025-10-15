import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  Calendar,
  CheckCircle2,
  XCircle,
  Clock,
  Users,
  TrendingUp,
} from 'lucide-react';
import { appointmentsApi } from '@/lib/api';
import { PageTransition } from '@/components/PageTransition';
import { StatCard } from '@/components/StatCard';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { useLanguage } from '@/contexts/LanguageContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts';

const COLORS = ['hsl(var(--primary))', 'hsl(var(--accent))', 'hsl(var(--success))', 'hsl(var(--warning))', 'hsl(var(--destructive))'];

export default function Dashboard() {
  const { t } = useLanguage();

  const { data: stats, isLoading } = useQuery({
    queryKey: ['appointmentStats'],
    queryFn: () => appointmentsApi.statistics(),
  });

  if (isLoading) {
    return (
      <PageTransition>
        <LoadingSpinner size="lg" />
      </PageTransition>
    );
  }

  const statsData = stats?.data || {};

  const statisticsCards = [
    {
      title: t('total_appointments', { en: 'Total Appointments', ar: 'إجمالي المواعيد' }),
      value: statsData.total || 0,
      icon: Calendar,
      trend: 12,
    },
    {
      title: t('completed', { en: 'Completed', ar: 'مكتمل' }),
      value: statsData.completed || 0,
      icon: CheckCircle2,
      trend: 8,
    },
    {
      title: t('cancelled', { en: 'Cancelled', ar: 'ملغى' }),
      value: statsData.cancelled || 0,
      icon: XCircle,
      trend: -3,
    },
    {
      title: t('upcoming', { en: 'Upcoming', ar: 'قادم' }),
      value: statsData.upcoming || 0,
      icon: Clock,
      trend: 15,
    },
  ];

  // Mock data for charts
  const appointmentsPerDay = [
    { day: t('mon', { en: 'Mon', ar: 'الإثنين' }), count: 12 },
    { day: t('tue', { en: 'Tue', ar: 'الثلاثاء' }), count: 19 },
    { day: t('wed', { en: 'Wed', ar: 'الأربعاء' }), count: 15 },
    { day: t('thu', { en: 'Thu', ar: 'الخميس' }), count: 22 },
    { day: t('fri', { en: 'Fri', ar: 'الجمعة' }), count: 18 },
    { day: t('sat', { en: 'Sat', ar: 'السبت' }), count: 25 },
    { day: t('sun', { en: 'Sun', ar: 'الأحد' }), count: 14 },
  ];

  const appointmentsByStatus = [
    { name: t('scheduled', { en: 'Scheduled', ar: 'مجدول' }), value: 45 },
    { name: t('completed', { en: 'Completed', ar: 'مكتمل' }), value: 30 },
    { name: t('cancelled', { en: 'Cancelled', ar: 'ملغى' }), value: 15 },
    { name: t('no_show', { en: 'No Show', ar: 'لم يحضر' }), value: 10 },
  ];

  const weeklyTrend = [
    { week: 'Week 1', appointments: 45 },
    { week: 'Week 2', appointments: 52 },
    { week: 'Week 3', appointments: 48 },
    { week: 'Week 4', appointments: 65 },
  ];

  return (
    <PageTransition>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <motion.h1
            className="text-3xl font-bold text-foreground"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4 }}
          >
            {t('dashboard', { en: 'Dashboard', ar: 'لوحة التحكم' })}
          </motion.h1>
          <motion.p
            className="text-muted-foreground mt-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            {t('dashboard_subtitle', {
              en: 'Overview of your clinic appointments and statistics',
              ar: 'نظرة عامة على مواعيد العيادة والإحصائيات',
            })}
          </motion.p>
        </div>

        {/* Statistics Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {statisticsCards.map((stat, index) => (
            <StatCard key={stat.title} {...stat} index={index} />
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid gap-6 md:grid-cols-2">
          {/* Bar Chart - Appointments per Day */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-primary" />
                  {t('appointments_per_day', {
                    en: 'Appointments Per Day',
                    ar: 'المواعيد لكل يوم',
                  })}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={appointmentsPerDay}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis dataKey="day" stroke="hsl(var(--muted-foreground))" />
                    <YAxis stroke="hsl(var(--muted-foreground))" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                      }}
                    />
                    <Bar dataKey="count" fill="hsl(var(--primary))" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>

          {/* Pie Chart - Status Distribution */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-primary" />
                  {t('appointments_by_status', {
                    en: 'Appointments by Status',
                    ar: 'المواعيد حسب الحالة',
                  })}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={appointmentsByStatus}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="hsl(var(--primary))"
                      dataKey="value"
                    >
                      {appointmentsByStatus.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Line Chart - Weekly Trend */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary" />
                {t('weekly_trend', { en: 'Weekly Appointment Trend', ar: 'اتجاه المواعيد الأسبوعي' })}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={weeklyTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="week" stroke="hsl(var(--muted-foreground))" />
                  <YAxis stroke="hsl(var(--muted-foreground))" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="appointments"
                    stroke="hsl(var(--primary))"
                    strokeWidth={3}
                    dot={{ fill: 'hsl(var(--primary))', r: 6 }}
                    activeDot={{ r: 8 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </PageTransition>
  );
}
