'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { toast } from 'sonner';
import { Loader2, Upload, X, CheckCircle, AlertCircle, Image as ImageIcon } from 'lucide-react';

import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { cn, formatBytes } from '@/lib/utils';

const MAX_FILE_SIZE = Number(process.env.NEXT_PUBLIC_MAX_FILE_SIZE || 104857600);
const MAX_FILES = Number(process.env.NEXT_PUBLIC_MAX_FILES || 50);
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface SelectedFile {
	file: File;
	previewUrl: string;
	size: number;
}

type JobStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';

export default function ImageToPdfPage() {
	const [files, setFiles] = useState<SelectedFile[]>([]);
	const [outputName, setOutputName] = useState('images.pdf');
	const [uploading, setUploading] = useState(false);
	const [converting, setConverting] = useState(false);
	const [jobId, setJobId] = useState<string | null>(null);
	const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
	const [resultUrl, setResultUrl] = useState<string | null>(null);
	const [error, setError] = useState<string | null>(null);

	const hasFiles = files.length > 0;

	const onDrop = useCallback(
		(acceptedFiles: File[]) => {
			if (!acceptedFiles.length) return;

			const remainingSlots = MAX_FILES - files.length;
			const sliced = acceptedFiles.slice(0, remainingSlots);

			const mapped = sliced.map((file) => ({
				file,
				previewUrl: URL.createObjectURL(file),
				size: file.size,
			}));

			setFiles((prev) => [...prev, ...mapped]);

			if (acceptedFiles.length > sliced.length) {
				toast.warning(`Only the first ${remainingSlots} files were added (max ${MAX_FILES}).`);
			}
		},
		[files.length],
	);

	const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
		accept: { 'image/*': [] },
		onDrop,
		maxSize: MAX_FILE_SIZE,
		multiple: true,
	});

	useEffect(() => {
		fileRejections.forEach(({ file, errors }) => {
			const reason = errors.map((e) => e.message).join(', ');
			toast.error(`${file.name}: ${reason}`);
		});
	}, [fileRejections]);

	useEffect(() => {
		return () => {
			files.forEach((item) => URL.revokeObjectURL(item.previewUrl));
		};
	}, [files]);

	const clearState = () => {
		setJobId(null);
		setJobStatus(null);
		setResultUrl(null);
		setError(null);
	};

	const handleRemoveFile = (index: number) => {
		URL.revokeObjectURL(files[index].previewUrl);
		setFiles((prev) => prev.filter((_, i) => i !== index));
	};

	const handleConvert = async () => {
		if (!hasFiles) {
			toast.error('Add at least one image to continue.');
			return;
		}

		clearState();
		setUploading(true);

		try {
			const uploadRes = await apiClient.uploadFiles(files.map((item) => item.file));
			const fileIds: string[] = uploadRes.data?.file_ids;

			if (!fileIds || !fileIds.length) {
				throw new Error('Upload failed. Please try again.');
			}

			setUploading(false);
			setConverting(true);

			const convertRes = await apiClient.convertImagesToPDF(fileIds, outputName);
			const newJobId: string | undefined = convertRes.data?.job_id;

			if (!newJobId) {
				throw new Error('Unable to start conversion job.');
			}

			setJobId(newJobId);
			setJobStatus('pending');
			toast.success('Conversion started. Processing your images...');
		} catch (err: any) {
			const message = err?.response?.data?.detail || err?.message || 'Unexpected error';
			setError(message);
			toast.error(message);
		} finally {
			setUploading(false);
			setConverting(false);
		}
	};

	useEffect(() => {
		if (!jobId || !jobStatus || ['completed', 'failed', 'cancelled'].includes(jobStatus)) {
			return;
		}

		const interval = setInterval(async () => {
			try {
				const res = await apiClient.getJobStatus(jobId);
				const { status, result_url: urlFromApi, error_message: errMsg } = res.data;

				setJobStatus(status);

				if (status === 'completed' && urlFromApi) {
					const fullUrl = urlFromApi.startsWith('http') ? urlFromApi : `${API_BASE_URL}${urlFromApi}`;
					setResultUrl(fullUrl);

					// Automatically trigger download
					const link = document.createElement('a');
					link.href = fullUrl;
					link.download = outputName || 'images.pdf';
					document.body.appendChild(link);
					link.click();
					document.body.removeChild(link);

					toast.success('Your PDF has been downloaded.');
				}

				if (status === 'failed' && errMsg) {
					setError(errMsg);
					toast.error(errMsg);
				}
			} catch (err: any) {
				const message = err?.response?.data?.detail || 'Unable to check job status';
				setError(message);
			}
		}, 2000);

		return () => clearInterval(interval);
	}, [jobId, jobStatus, outputName]);

	const totalSize = useMemo(() => files.reduce((sum, f) => sum + f.size, 0), [files]);

	const statusLabel = useMemo(() => {
		if (!jobStatus) return 'Idle';
		if (jobStatus === 'pending') return 'Queued';
		if (jobStatus === 'processing') return 'Processing';
		if (jobStatus === 'completed') return 'Completed';
		if (jobStatus === 'failed') return 'Failed';
		if (jobStatus === 'cancelled') return 'Cancelled';
		return jobStatus;
	}, [jobStatus]);

	return (
		<div className='bg-muted/40 py-12'>
			<div className='container max-w-5xl space-y-10'>
				<div className='rounded-3xl border bg-card/80 p-8 shadow-lg backdrop-blur'>
					<div className='flex items-start gap-4'>
						<div className='flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10'>
							<ImageIcon className='h-6 w-6 text-primary' />
						</div>
						<div className='space-y-2'>
							<h1 className='text-2xl font-bold md:text-3xl'>Image to PDF</h1>
							<p className='text-muted-foreground'>
								Upload multiple images (JPG, PNG, WebP, HEIC, more) and we will combine them into a
								single PDF while preserving order.
							</p>
						</div>
					</div>

					<div className='mt-8 grid gap-8 lg:grid-cols-[1.6fr_1fr]'>
						<div className='space-y-6'>
							<div
								{...getRootProps({
									className: cn(
										'flex min-h-[220px] cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed bg-muted/60 p-6 text-center transition hover:border-primary/60 hover:bg-muted',
										isDragActive ? 'border-primary/80 bg-primary/5' : 'border-muted-foreground/30',
									),
								})}
							>
								<input {...getInputProps()} />
								<div className='flex flex-col items-center gap-3'>
									<div className='flex h-14 w-14 items-center justify-center rounded-full bg-primary/10 text-primary'>
										{uploading || converting ? (
											<Loader2 className='h-7 w-7 animate-spin' />
										) : (
											<Upload className='h-7 w-7' />
										)}
									</div>
									<div className='space-y-1'>
										<p className='text-lg font-semibold'>Drop images here or click to browse</p>
										<p className='text-sm text-muted-foreground'>
											Supports JPG, PNG, WebP, HEIC, GIF. Up to {MAX_FILES} files,{' '}
											{formatBytes(MAX_FILE_SIZE)} each.
										</p>
									</div>
								</div>
							</div>

							{hasFiles && (
								<div className='rounded-xl border bg-background/60 p-4 shadow-sm'>
									<div className='flex items-center justify-between'>
										<div className='space-y-1'>
											<p className='text-sm font-medium'>Selected files ({files.length})</p>
											<p className='text-xs text-muted-foreground'>
												Total size: {formatBytes(totalSize)}
											</p>
										</div>
										<Button variant='ghost' size='sm' onClick={() => setFiles([])}>
											Clear all
										</Button>
									</div>
									<div className='mt-4 space-y-3'>
										{files.map((item, index) => (
											<div
												key={`${item.file.name}-${index}`}
												className='flex items-center justify-between rounded-lg border bg-card/60 px-3 py-2'
											>
												<div className='flex items-center gap-3'>
													<div className='flex h-10 w-10 items-center justify-center overflow-hidden rounded-md bg-muted'>
														<img
															src={item.previewUrl}
															alt={item.file.name}
															className='h-10 w-10 object-cover'
														/>
													</div>
													<div>
														<p className='text-sm font-medium leading-tight'>
															{item.file.name}
														</p>
														<p className='text-xs text-muted-foreground'>
															{formatBytes(item.size)}
														</p>
													</div>
												</div>
												<button
													type='button'
													className='text-muted-foreground transition hover:text-destructive'
													onClick={() => handleRemoveFile(index)}
													aria-label={`Remove ${item.file.name}`}
												>
													<X className='h-5 w-5' />
												</button>
											</div>
										))}
									</div>
								</div>
							)}
						</div>

						<div className='rounded-2xl border bg-background/80 p-5 shadow-sm'>
							<div className='space-y-4'>
								<div>
									<label className='text-sm font-medium text-muted-foreground'>
										Output file name
									</label>
									<input
										type='text'
										value={outputName}
										onChange={(e) => setOutputName(e.target.value)}
										className='mt-2 w-full rounded-lg border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary'
										placeholder='images.pdf'
									/>
								</div>

								<div className='rounded-lg border bg-muted/40 p-3 text-sm text-muted-foreground'>
									<p>Tips:</p>
									<ul className='list-disc space-y-1 pl-5'>
										<li>Files keep the order you add them.</li>
										<li>Use high-quality images for best PDF results.</li>
										<li>We clean temporary uploads automatically.</li>
									</ul>
								</div>

								<Button
									className='w-full'
									onClick={handleConvert}
									disabled={uploading || converting || !hasFiles}
								>
									{(uploading || converting) && <Loader2 className='mr-2 h-4 w-4 animate-spin' />}
									{uploading
										? 'Uploading...'
										: converting
											? 'Starting conversion...'
											: 'Convert to PDF'}
								</Button>

								<div className='rounded-lg border bg-muted/40 p-4'>
									<div className='flex items-center gap-2 text-sm font-medium'>
										{jobStatus === 'completed' && (
											<CheckCircle className='h-4 w-4 text-emerald-500' />
										)}
										{jobStatus === 'failed' && <AlertCircle className='h-4 w-4 text-destructive' />}
										<span>Status: {statusLabel}</span>
									</div>
									{error && <p className='mt-2 text-sm text-destructive'>{error}</p>}
									{resultUrl && (
										<a
											href={resultUrl}
											className='mt-3 inline-flex items-center text-sm font-medium text-primary hover:underline'
										>
											Download PDF
										</a>
									)}
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
}
