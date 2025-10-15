import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, FileText, Download, CheckCircle, XCircle, Trash2 } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import apiService from '@/services/api';
import { toast } from 'sonner';

export default function Documents() {
  const { t } = useLanguage();
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      // In real scenario, you'd filter by patient or get all
      const data = await apiService.getDocuments('all');
      setDocuments(data.results || data || []);
    } catch (error) {
      console.error('Failed to load documents:', error);
      // Mock data for development
      setDocuments([
        {
          id: '1',
          document_type: 'Medical Report',
          upload_date: '2024-01-15',
          is_verified: true,
          patient_name: 'John Doe',
        },
        {
          id: '2',
          document_type: 'Lab Results',
          upload_date: '2024-01-20',
          is_verified: false,
          patient_name: 'Jane Smith',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    try {
      for (const file of Array.from(files)) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('document_type', file.name);
        formData.append('patient', '1'); // In real scenario, select patient

        await apiService.uploadDocument(formData);
      }
      toast.success('Documents uploaded successfully');
      loadDocuments();
    } catch (error) {
      toast.error(t('error-occurred'));
      console.error('Failed to upload documents:', error);
    } finally {
      setUploading(false);
    }
  };

  const handleVerify = async (id: string, verify: boolean) => {
    try {
      if (verify) {
        await apiService.verifyDocument(id);
        toast.success('Document verified');
      } else {
        await apiService.unverifyDocument(id);
        toast.success('Document unverified');
      }
      loadDocuments();
    } catch (error) {
      toast.error(t('error-occurred'));
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm(t('confirm-delete'))) return;

    try {
      await apiService.deleteDocument(id);
      toast.success('Document deleted');
      loadDocuments();
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
        className="rounded-2xl bg-gradient-hero p-8 text-white shadow-large"
      >
        <h1 className="text-3xl font-bold mb-2">{t('documents')}</h1>
        <p className="text-white/90">Manage patient documents and files</p>
      </motion.div>

      {/* Upload Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="shadow-soft border-2 border-dashed border-border hover:border-primary/50 transition-all">
          <CardContent className="p-8">
            <label htmlFor="file-upload" className="cursor-pointer block">
              <div className="flex flex-col items-center justify-center space-y-3">
                <div className="w-16 h-16 rounded-full bg-gradient-primary/10 flex items-center justify-center">
                  <Upload className="h-8 w-8 text-primary" />
                </div>
                <div className="text-center">
                  <p className="font-semibold text-lg">{t('drag-drop')}</p>
                  <p className="text-sm text-muted-foreground">
                    PDF, DOCX, PNG, JPG up to 10MB
                  </p>
                </div>
                <Button
                  type="button"
                  className="bg-gradient-primary hover:shadow-glow"
                  disabled={uploading}
                >
                  <Upload className="h-4 w-4 mr-2" />
                  {uploading ? t('loading') : t('upload-document')}
                </Button>
              </div>
              <input
                id="file-upload"
                type="file"
                multiple
                className="hidden"
                onChange={handleFileUpload}
                accept=".pdf,.doc,.docx,.png,.jpg,.jpeg"
              />
            </label>
          </CardContent>
        </Card>
      </motion.div>

      {/* Documents List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card className="shadow-soft">
          <CardHeader>
            <CardTitle>All Documents</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p className="text-center py-8 text-muted-foreground">{t('loading')}</p>
            ) : documents.length === 0 ? (
              <p className="text-center py-8 text-muted-foreground">No documents found</p>
            ) : (
              <div className="space-y-3">
                {documents.map((doc, index) => (
                  <motion.div
                    key={doc.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="flex items-center justify-between p-4 border border-border rounded-lg hover:border-primary/50 hover:shadow-soft transition-all"
                  >
                    <div className="flex items-center gap-4 flex-1">
                      <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                        <FileText className="h-6 w-6 text-primary" />
                      </div>
                      <div className="flex-1">
                        <p className="font-semibold">{doc.document_type}</p>
                        <p className="text-sm text-muted-foreground">
                          {doc.patient_name} • {doc.upload_date}
                        </p>
                      </div>
                      <Badge
                        variant={doc.is_verified ? 'default' : 'secondary'}
                        className={doc.is_verified ? 'bg-success' : ''}
                      >
                        {doc.is_verified ? t('verified') : 'Pending'}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleVerify(doc.id, !doc.is_verified)}
                      >
                        {doc.is_verified ? (
                          <XCircle className="h-4 w-4 text-warning" />
                        ) : (
                          <CheckCircle className="h-4 w-4 text-success" />
                        )}
                      </Button>
                      <Button variant="ghost" size="icon">
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(doc.id)}
                        className="text-destructive hover:text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
