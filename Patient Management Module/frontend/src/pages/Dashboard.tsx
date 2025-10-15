import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Users, UserCheck, UserX, UserPlus } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { KPICard } from '@/components/patients/KPICard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import apiService from '@/services/api';
import { toast } from 'sonner';

export default function Dashboard() {
  const { t } = useLanguage();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    try {
      setLoading(true);
      const data = await apiService.getPatientStatistics();
      setStats(data);
    } catch (error) {
      toast.error(t('error-occurred'));
      console.error('Failed to load statistics:', error);
      // Mock data for development
      setStats({
        total: 1248,
        active: 1102,
        inactive: 146,
        new_this_month: 89,
        male: 612,
        female: 636,
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-lg text-muted-foreground">{t('loading')}</div>
      </div>
    );
  }

  const genderData = [
    { name: t('male-patients'), value: stats?.male || 0, color: 'hsl(199 89% 48%)' },
    { name: t('female-patients'), value: stats?.female || 0, color: 'hsl(172 66% 50%)' },
  ];

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl bg-gradient-hero p-8 text-white shadow-large"
      >
        <h1 className="text-3xl font-bold mb-2">{t('dashboard')}</h1>
        <p className="text-white/90">{t('patient-statistics')}</p>
      </motion.div>

      {/* KPI Cards */}
      <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
        <KPICard
          title={t('total-patients')}
          value={stats?.total || 0}
          icon={Users}
          trend={{ value: 12, positive: true }}
          delay={0}
        />
        <KPICard
          title={t('active-patients')}
          value={stats?.active || 0}
          icon={UserCheck}
          trend={{ value: 8, positive: true }}
          delay={0.1}
        />
        <KPICard
          title={t('inactive-patients')}
          value={stats?.inactive || 0}
          icon={UserX}
          trend={{ value: 3, positive: false }}
          delay={0.2}
        />
        <KPICard
          title={t('new-registrations')}
          value={stats?.new_this_month || 0}
          icon={UserPlus}
          trend={{ value: 15, positive: true }}
          delay={0.3}
        />
      </div>

      {/* Charts */}
      <div className="grid gap-6 grid-cols-1 lg:grid-cols-2">
        {/* Gender Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="shadow-soft hover:shadow-medium transition-all">
            <CardHeader>
              <CardTitle>{t('gender-distribution')}</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={genderData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {genderData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card className="shadow-soft hover:shadow-medium transition-all">
            <CardHeader>
              <CardTitle>{t('recent-activity')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[1, 2, 3, 4, 5].map((item, index) => (
                  <motion.div
                    key={item}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 + index * 0.1 }}
                    className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <div className="w-2 h-2 rounded-full bg-primary animate-pulse-glow" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">New patient registered</p>
                      <p className="text-xs text-muted-foreground">{item} minutes ago</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
