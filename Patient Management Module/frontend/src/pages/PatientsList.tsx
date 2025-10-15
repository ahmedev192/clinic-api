import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Search, Eye, Edit, Trash2, Plus } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import apiService from '@/services/api';
import { toast } from 'sonner';

export default function PatientsList() {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [patients, setPatients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    try {
      setLoading(true);
      const data = await apiService.getPatients();
      setPatients(data.results || data || []);
    } catch (error) {
      toast.error(t('error-occurred'));
      console.error('Failed to load patients:', error);
      // Mock data for development
      setPatients([
        {
          id: '1',
          first_name_en: 'John',
          last_name_en: 'Doe',
          phone_primary: '+1234567890',
          gender: 'M',
          is_active: true,
        },
        {
          id: '2',
          first_name_en: 'Jane',
          last_name_en: 'Smith',
          phone_primary: '+1987654321',
          gender: 'F',
          is_active: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadPatients();
      return;
    }

    try {
      const data = await apiService.searchPatients(searchQuery);
      setPatients(data.results || data || []);
    } catch (error) {
      toast.error(t('error-occurred'));
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm(t('confirm-delete'))) return;

    try {
      await apiService.deletePatient(id);
      toast.success(t('success'));
      loadPatients();
    } catch (error) {
      toast.error(t('error-occurred'));
    }
  };

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl bg-gradient-hero p-8 text-white shadow-large flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold mb-2">{t('patients-list')}</h1>
          <p className="text-white/90">Manage all patient records</p>
        </div>
        <Button
          onClick={() => navigate('/patients/new')}
          className="bg-white text-primary hover:bg-white/90 shadow-glow"
        >
          <Plus className="h-4 w-4 mr-2" />
          {t('add-patient')}
        </Button>
      </motion.div>

      {/* Search Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="p-4 shadow-soft">
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder={t('search-patients')}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="pl-10"
              />
            </div>
            <Button onClick={handleSearch}>{t('search')}</Button>
          </div>
        </Card>
      </motion.div>

      {/* Patients Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card className="shadow-soft overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('name')}</TableHead>
                <TableHead>{t('phone')}</TableHead>
                <TableHead>{t('gender')}</TableHead>
                <TableHead>{t('status')}</TableHead>
                <TableHead className="text-right">{t('actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8">
                    {t('loading')}
                  </TableCell>
                </TableRow>
              ) : patients.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8">
                    {t('no-patients')}
                  </TableCell>
                </TableRow>
              ) : (
                patients.map((patient, index) => (
                  <motion.tr
                    key={patient.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="hover:bg-muted/50 transition-colors"
                  >
                    <TableCell className="font-medium">
                      {patient.first_name_en} {patient.last_name_en}
                    </TableCell>
                    <TableCell>{patient.phone_primary}</TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {patient.gender === 'M' ? t('male') : t('female')}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={patient.is_active ? 'default' : 'secondary'}
                        className={patient.is_active ? 'bg-success' : ''}
                      >
                        {patient.is_active ? t('active') : t('inactive')}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => navigate(`/patients/${patient.id}`)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => navigate(`/patients/${patient.id}/edit`)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(patient.id)}
                          className="text-destructive hover:text-destructive"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </motion.tr>
                ))
              )}
            </TableBody>
          </Table>
        </Card>
      </motion.div>
    </div>
  );
}
