import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Activity, User, Calendar, AlertCircle } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import apiService from '@/services/api';

export default function AuditLogs() {
  const { t } = useLanguage();
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    try {
      setLoading(true);
      const data = await apiService.getAuditLogs();
      setLogs(data.results || data || []);
    } catch (error) {
      console.error('Failed to load audit logs:', error);
      // Mock data for development
      setLogs([
        {
          id: '1',
          action: 'CREATE',
          entity_type: 'Patient',
          entity_id: '1',
          user: 'Admin User',
          timestamp: '2024-01-20 14:30:25',
          details: 'Created new patient record',
        },
        {
          id: '2',
          action: 'UPDATE',
          entity_type: 'Patient',
          entity_id: '1',
          user: 'Admin User',
          timestamp: '2024-01-20 15:45:10',
          details: 'Updated patient contact information',
        },
        {
          id: '3',
          action: 'CREATE',
          entity_type: 'Document',
          entity_id: '5',
          user: 'Nurse Jane',
          timestamp: '2024-01-20 16:20:00',
          details: 'Uploaded medical report',
        },
        {
          id: '4',
          action: 'DELETE',
          entity_type: 'Patient',
          entity_id: '12',
          user: 'Admin User',
          timestamp: '2024-01-19 11:15:30',
          details: 'Deleted inactive patient record',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'CREATE':
        return 'bg-success';
      case 'UPDATE':
        return 'bg-primary';
      case 'DELETE':
        return 'bg-destructive';
      default:
        return 'bg-secondary';
    }
  };

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'CREATE':
        return Activity;
      case 'UPDATE':
        return AlertCircle;
      case 'DELETE':
        return AlertCircle;
      default:
        return Activity;
    }
  };

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl bg-gradient-hero p-8 text-white shadow-large"
      >
        <h1 className="text-3xl font-bold mb-2">{t('audit-logs')}</h1>
        <p className="text-white/90">Track all system activities and changes</p>
      </motion.div>

      {/* Logs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="shadow-soft">
          <CardHeader>
            <CardTitle>{t('recent-activity')}</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p className="text-center py-8 text-muted-foreground">{t('loading')}</p>
            ) : logs.length === 0 ? (
              <p className="text-center py-8 text-muted-foreground">No audit logs found</p>
            ) : (
              <div className="space-y-4">
                {logs.map((log, index) => {
                  const Icon = getActionIcon(log.action);
                  
                  return (
                    <motion.div
                      key={log.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="flex items-start gap-4 p-4 border border-border rounded-lg hover:border-primary/50 hover:shadow-soft transition-all"
                    >
                      <div className={`p-2 rounded-lg ${getActionColor(log.action)}/10`}>
                        <Icon className={`h-5 w-5 text-${getActionColor(log.action)}`} />
                      </div>

                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <Badge className={getActionColor(log.action)}>
                                {log.action}
                              </Badge>
                              <span className="text-sm font-semibold">
                                {log.entity_type} #{log.entity_id}
                              </span>
                            </div>
                            <p className="text-sm">{log.details}</p>
                          </div>
                        </div>

                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <User className="h-3 w-3" />
                            <span>{log.user}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            <span>{log.timestamp}</span>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
