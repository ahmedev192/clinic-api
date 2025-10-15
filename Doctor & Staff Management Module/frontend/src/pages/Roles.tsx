import { motion } from 'framer-motion';
import { Shield, Users } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const mockRoles = [
  { id: 1, name: 'Nurse', name_ar: 'ممرض', count: 8, color: 'bg-primary' },
  { id: 2, name: 'Receptionist', name_ar: 'موظف استقبال', count: 4, color: 'bg-accent' },
  { id: 3, name: 'Lab Technician', name_ar: 'فني مختبر', count: 3, color: 'bg-success' },
  { id: 4, name: 'Pharmacist', name_ar: 'صيدلي', count: 2, color: 'bg-warning' },
  { id: 5, name: 'Admin', name_ar: 'مسؤول', count: 2, color: 'bg-destructive' },
];

export default function Roles() {
  const { t, language } = useLanguage();

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold mb-2">{t('roles')}</h1>
        <p className="text-muted-foreground">Manage staff roles and permissions</p>
      </motion.div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {mockRoles.map((role, index) => (
          <motion.div
            key={role.id}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ y: -4 }}
          >
            <Card className="hover:shadow-medium transition-all border-border/50">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className={`flex h-12 w-12 items-center justify-center rounded-lg ${role.color} bg-opacity-20`}>
                    <Shield className={`h-6 w-6 ${role.color.replace('bg-', 'text-')}`} />
                  </div>
                  <div className="flex-1">
                    <CardTitle className="text-lg">
                      {language === 'en' ? role.name : role.name_ar}
                    </CardTitle>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Users className="h-4 w-4" />
                    <span>{role.count} members</span>
                  </div>
                  <Badge>{role.count}</Badge>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
