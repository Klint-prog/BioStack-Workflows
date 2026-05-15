nextflow.enable.dsl=2

params.input = params.input ?: 'data/raw'
params.reference = params.reference ?: 'data/reference/reference.fa'
params.outdir = params.outdir ?: 'results/variant-calling-basic'
params.run_id = params.run_id ?: 'manual-run'

workflow {
    Channel
        .fromPath("${params.input}/*.{bam,cram,vcf,vcf.gz}", checkIfExists: false)
        .ifEmpty([])
        .set { variant_inputs_ch }

    VARIANT_CALLING_DEMO(variant_inputs_ch)

    emit:
    variant_results = VARIANT_CALLING_DEMO.out
}

process VARIANT_CALLING_DEMO {
    tag { sample.simpleName }
    publishDir "${params.outdir}/variants", mode: 'copy'

    input:
    path sample

    output:
    path "${sample.simpleName}.variant-calling-demo.txt"

    script:
    """
    echo "BioStack variant-calling basic demo" > ${sample.simpleName}.variant-calling-demo.txt
    echo "run_id=${params.run_id}" >> ${sample.simpleName}.variant-calling-demo.txt
    echo "input=${sample}" >> ${sample.simpleName}.variant-calling-demo.txt
    echo "reference=${params.reference}" >> ${sample.simpleName}.variant-calling-demo.txt
    echo "variant-calling placeholder: replace with validated BWA/Samtools/BCFtools/GATK steps in production pipelines" >> ${sample.simpleName}.variant-calling-demo.txt
    """
}
