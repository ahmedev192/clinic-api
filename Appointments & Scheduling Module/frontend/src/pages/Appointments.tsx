import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Search, Filter, Calendar as CalendarIcon } from 'lucide-react';
import { appointmentsApi } from '@/lib/api';
import { PageTransition } from '@/components/PageTransition';
import { LoadingSpinner, LoadingSkeleton } from '@/components/LoadingSpinner';
import { StatusBadge } from '@/components/StatusBadge';
import { useLanguage } from '@/contexts/LanguageContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';

export default function Appointments() {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ['appointments', page, searchQuery],
    queryFn: () =>
      searchQuery
        ? appointmentsApi.search({ q: searchQuery, page })
        : appointmentsApi.list({ page }),
  });

  const appointments = data?.data?.results || [];

  return (
    <PageTransition>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <motion.h1
              className="text-3xl font-bold text-foreground"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              {t('appointments', { en: 'Appointments', ar: 'المواعيد' })}
            </motion.h1>
            <motion.p
              className="text-muted-foreground mt-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
            >
              {t('manage_appointments', {
                en: 'Manage and track all clinic appointments',
                ar: 'إدارة وتتبع جميع مواعيد العيادة',
              })}
            </motion.p>
          </div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            <Button
              onClick={() => navigate('/appointments/new')}
              className="gap-2"
            >
              <Plus className="h-4 w-4" />
              {t('new_appointment', { en: 'New Appointment', ar: 'موعد جديد' })}
            </Button>
          </motion.div>
        </div>

        {/* Search and Filters */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="flex flex-col md:flex-row gap-4"
        >
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder={t('search_placeholder', {
                en: 'Search by patient name, doctor, or appointment ID...',
                ar: 'البحث باسم المريض، الطبيب، أو رقم الموعد...',
              })}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <Button variant="outline" className="gap-2">
            <Filter className="h-4 w-4" />
            {t('filters', { en: 'Filters', ar: 'الفلاتر' })}
          </Button>
        </motion.div>

        {/* Appointments Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card>
            <CardContent className="p-0">
              {isLoading ? (
                <div className="p-6">
                  <LoadingSkeleton count={5} />
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>{t('id', { en: 'ID', ar: 'الرقم' })}</TableHead>
                        <TableHead>{t('patient', { en: 'Patient', ar: 'المريض' })}</TableHead>
                        <TableHead>{t('doctor', { en: 'Doctor', ar: 'الطبيب' })}</TableHead>
                        <TableHead>{t('date', { en: 'Date', ar: 'التاريخ' })}</TableHead>
                        <TableHead>{t('time', { en: 'Time', ar: 'الوقت' })}</TableHead>
                        <TableHead>{t('status', { en: 'Status', ar: 'الحالة' })}</TableHead>
                        <TableHead>{t('actions', { en: 'Actions', ar: 'الإجراءات' })}</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <AnimatePresence mode="wait">
                        {appointments.map((appointment: any, index: number) => (
                          <motion.tr
                            key={appointment.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 20 }}
                            transition={{ delay: index * 0.05 }}
                            className="hover:bg-muted/50 cursor-pointer transition-colors"
                            onClick={() => navigate(`/appointments/${appointment.id}`)}
                          >
                            <TableCell className="font-medium">{appointment.id}</TableCell>
                            <TableCell>{appointment.patient_name || 'N/A'}</TableCell>
                            <TableCell>{appointment.doctor_name || 'N/A'}</TableCell>
                            <TableCell>
                              {appointment.date
                                ? format(new Date(appointment.date), 'MMM dd, yyyy')
                                : 'N/A'}
                            </TableCell>
                            <TableCell>{appointment.time || 'N/A'}</TableCell>
                            <TableCell>
                              <StatusBadge status={appointment.status || 'scheduled'} />
                            </TableCell>
                            <TableCell>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  navigate(`/appointments/${appointment.id}`);
                                }}
                              >
                                {t('view', { en: 'View', ar: 'عرض' })}
                              </Button>
                            </TableCell>
                          </motion.tr>
                        ))}
                      </AnimatePresence>
                    </TableBody>
                  </Table>

                  {appointments.length === 0 && (
                    <div className="py-12 text-center">
                      <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.3 }}
                      >
                        <CalendarIcon className="h-16 w-16 text-muted-foreground mx-auto mb-4 opacity-50" />
                        <h3 className="text-lg font-semibold text-foreground mb-2">
                          {t('no_appointments', {
                            en: 'No appointments found',
                            ar: 'لا توجد مواعيد',
                          })}
                        </h3>
                        <p className="text-muted-foreground">
                          {t('no_appointments_desc', {
                            en: 'Get started by creating a new appointment',
                            ar: 'ابدأ بإنشاء موعد جديد',
                          })}
                        </p>
                      </motion.div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Pagination */}
        {data?.data?.count > 10 && (
          <motion.div
            className="flex justify-center gap-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            <Button
              variant="outline"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              {t('previous', { en: 'Previous', ar: 'السابق' })}
            </Button>
            <Button
              variant="outline"
              onClick={() => setPage((p) => p + 1)}
              disabled={!data?.data?.next}
            >
              {t('next', { en: 'Next', ar: 'التالي' })}
            </Button>
          </motion.div>
        )}
      </div>
    </PageTransition>
  );
}
