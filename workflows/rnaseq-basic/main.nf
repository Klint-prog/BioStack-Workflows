nextflow.enable.dsl=2

params.input = params.input ?: 'data/raw'
params.outdir = params.outdir ?: 'results/rnaseq-basic'
params.run_id = params.run_id ?: 'manual-run'

workflow {
    Channel
        .fromPath("${params.input}/*.{fastq,fq,fastq.gz,fq.gz}", checkIfExists: false)
        .ifEmpty([])
        .set { reads_ch }

    FASTQC_DEMO(reads_ch)

    emit:
    fastqc_results = FASTQC_DEMO.out
}

process FASTQC_DEMO {
    tag { reads.simpleName }
    publishDir "${params.outdir}/fastqc", mode: 'copy'

    input:
    path reads

    output:
    path "${reads.simpleName}.fastqc.txt"

    script:
    """
    echo "BioStack RNA-seq basic demo" > ${reads.simpleName}.fastqc.txt
    echo "run_id=${params.run_id}" >> ${reads.simpleName}.fastqc.txt
    echo "input=${reads}" >> ${reads.simpleName}.fastqc.txt
    echo "fastqc placeholder: replace with real FastQC execution in validated pipelines" >> ${reads.simpleName}.fastqc.txt
    """
}
