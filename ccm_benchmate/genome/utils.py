import pandas as pd
import json

from sqlalchemy import MetaData, insert

def parse_gtf_attributes(attributes_str):
    """
    parse the gtf attributes column that is the last one
    :param attributes_str:
    :return:
    """
    attributes = {}
    for item in attributes_str.strip().split(';'):
        item = item.strip()
        if not item:
            continue
        parts = item.split(' ', 1)
        if len(parts) == 2:
            key = parts[0].strip()
            value = parts[1].strip().strip('"')
            attributes[key] = value
    return attributes

def find_containing_temp_exon_id(transcript_id_str, feature_start, feature_end, data_cache):
    """
    we are generating temp exon ids, the databse will be able to store multiple genomes so we will need to use
    postgresqls returning feature but in the meantime we will need some sort of temp id
    :param transcript_id_str:
    :param feature_start:
    :param feature_end:
    :param data_cache:
    :return:
    """
    if transcript_id_str not in data_cache['exons_by_transcript']:
        return None
    for exon_start, exon_end, temp_exon_id in data_cache['exons_by_transcript'][transcript_id_str]:
        if exon_start <= feature_start and exon_end >= feature_end:
            return temp_exon_id
    return None

def parse_gtf(gtf_filepath):
    chrom_list = []
    gene_list = []
    transcript_list = []
    exon_list = []
    cds_list = []
    three_utr_list = []
    five_utr_list = []
    intron_list = []

    data_cache = {
        'chrom_names': set(),
        'processed_genes': set(),
        'processed_transcripts': set(),
        'exons_by_transcript': {},
        'temp_exon_id_counter': 0,
    }

    line_count = 0
    with open(gtf_filepath, 'r') as gtf_file:
        for line in gtf_file:
            line_count += 1
            if line.startswith('#') or not line.strip():
                continue
            fields = line.strip().split('\t')

            if len(fields) != 9:
                continue

            fields = line.strip().split('\t')
            chrom_name = fields[0]
            feature_type = fields[2]
            start = int(fields[3])
            end = int(fields[4])
            strand = fields[6]
            attributes_str = fields[8]
            attributes = parse_gtf_attributes(attributes_str)

            data_cache['chrom_names'].add(chrom_name)

            if feature_type == 'gene':
                gene_id_str = attributes.get('gene_id')
                if not gene_id_str: continue
                if gene_id_str not in data_cache['processed_genes']:
                    gene_list.append({
                        'gene_name': gene_id_str, 'chrom': chrom_name,
                        'start': start, 'end': end, 'strand': strand,
                        'annot': json.dumps(attributes)
                    })
                    data_cache['processed_genes'].add(gene_id_str)

            elif feature_type == 'transcript':
                transcript_id_str = attributes.get('transcript_id')
                gene_id_str = attributes.get('gene_id')
                if not transcript_id_str or not gene_id_str: continue
                if transcript_id_str not in data_cache['processed_transcripts']:
                    transcript_list.append({
                        'transcript_name': transcript_id_str, 'start': start, 'end': end,
                        'gtf_gene_id': gene_id_str, 'annot': json.dumps(attributes)
                    })
                    data_cache['processed_transcripts'].add(transcript_id_str)
                    data_cache['exons_by_transcript'][transcript_id_str] = []

            elif feature_type == 'exon':
                transcript_id_str = attributes.get('transcript_id')
                if not transcript_id_str: continue
                exon_rank = attributes.get('exon_number')
                exon_rank_int = int(exon_rank) if exon_rank and exon_rank.isdigit() else None
                exon_id_str = attributes.get('exon_id')
                data_cache['temp_exon_id_counter'] += 1
                temp_exon_id = data_cache['temp_exon_id_counter']
                exon_list.append({
                    'temp_exon_id': temp_exon_id, 'exon_name': exon_id_str,
                    'start': start, 'end': end, 'exon_rank': exon_rank_int,
                    'gtf_transcript_id': transcript_id_str
                })
                # Add exon to cache even if transcript wasn't seen first (might happen in odd GTFs)
                if transcript_id_str not in data_cache['exons_by_transcript']:
                    data_cache['exons_by_transcript'][transcript_id_str] = []
                data_cache['exons_by_transcript'][transcript_id_str].append((start, end, temp_exon_id))

            elif feature_type in ['CDS', 'three_prime_utr', 'five_prime_utr']:
                transcript_id_str = attributes.get('transcript_id')
                if not transcript_id_str: continue
                parent_temp_exon_id = find_containing_temp_exon_id(transcript_id_str, start, end, data_cache)
                if parent_temp_exon_id is None:
                    # Skip silently probably should raise a warning
                    continue

                if feature_type == 'CDS':
                    cds_list.append({'cds_name': attributes.get('protein_id'), 'start': start, 'end': end,
                                     'temp_exon_id': parent_temp_exon_id})
                elif feature_type == 'three_prime_utr':
                    three_utr_list.append({'start': start, 'end': end, 'temp_exon_id': parent_temp_exon_id})
                elif feature_type == 'five_prime_utr':
                    five_utr_list.append({'start': start, 'end': end, 'temp_exon_id': parent_temp_exon_id})

            # get introns
            for transcript_id_str, exon_info_list in data_cache['exons_by_transcript'].items():
                if len(exon_info_list) > 1:
                    sorted_exons = sorted(exon_info_list, key=lambda x: x[0])
                    for i in range(len(sorted_exons) - 1):
                        exon1_start, exon1_end, _ = sorted_exons[i]
                        exon2_start, exon2_end, _ = sorted_exons[i + 1]
                        intron_start = exon1_end + 1
                        intron_end = exon2_start - 1
                        if intron_start <= intron_end:
                            intron_list.append({
                                'gtf_transcript_id': transcript_id_str, 'intron_rank': i + 1,
                                'start': intron_start, 'end': intron_end
                            })

    df_chrom = pd.DataFrame({'chrom': list(data_cache['chrom_names'])})
    df_gene = pd.DataFrame(gene_list) if gene_list else pd.DataFrame(
        columns=['gene_name', 'chrom', 'start', 'end', 'strand', 'annot'])
    df_transcript = pd.DataFrame(transcript_list) if transcript_list else pd.DataFrame(
        columns=['transcript_name', 'start', 'end', 'gtf_gene_id', 'annot'])
    df_exon = pd.DataFrame(exon_list) if exon_list else pd.DataFrame(
        columns=['temp_exon_id', 'exon_name', 'start', 'end', 'exon_rank', 'gtf_transcript_id'])
    df_cds = pd.DataFrame(cds_list) if cds_list else pd.DataFrame(
        columns=['cds_name', 'start', 'end', 'temp_exon_id'])
    df_three_utr = pd.DataFrame(three_utr_list) if three_utr_list else pd.DataFrame(
        columns=['start', 'end', 'temp_exon_id'])
    df_five_utr = pd.DataFrame(five_utr_list) if five_utr_list else pd.DataFrame(
        columns=['start', 'end', 'temp_exon_id'])
    df_intron = pd.DataFrame(intron_list) if intron_list else pd.DataFrame(
        columns=['gtf_transcript_id', 'intron_rank', 'start', 'end'])

    return df_chrom, df_gene, df_transcript, df_exon, df_cds, df_three_utr, df_five_utr, df_intron


def insert_genome(df_chrom, df_gene, df_transcript, df_exon, df_cds, df_three_utr, df_five_utr, df_intron, engine):
    #instead of just doing df.to_sql I will need to move the records one by one and get their primary keys
    # to be used as foreign keys in other tables
    #TODO metadata
    metadata = MetaData(bind=engine)
    metadata.reflect()

    ChromTable = metadata.tables['chrom']
    GeneTable = metadata.tables['gene']
    TranscriptTable = metadata.tables['transcript']
    ExonTable = metadata.tables['exon']
    CdsTable = metadata.tables['cds']
    ThreeUTRTable = metadata.tables['three_utr']
    FiveUTRTable = metadata.tables['five_utr']

    with engine.connect() as connection:
        transaction = connection.begin()
        chrom_map = {}
        if not df_chrom.empty:
            chrom_data = df_chrom.to_dict('records')
            stmt = insert(ChromTable).values(chrom_data).returning(ChromTable.c.chrom_id, ChromTable.c.chrom)
            result = connection.execute(stmt)
            chrom_map = {row.chrom: row.chrom_id for row in result}

        gene_map = {}
        if not df_gene.empty:
            df_gene['chrom_id'] = df_gene['chrom'].map(chrom_map)
            df_gene_insert = df_gene[['gene_name', 'chrom_id', 'start', 'end', 'strand', 'annot']].dropna(
                subset=['chrom_id'])
            df_gene_insert['chrom_id'] = df_gene_insert['chrom_id'].astype(int)
            if not df_gene_insert.empty:
                gene_data = df_gene_insert.to_dict('records')
                stmt = insert(GeneTable).values(gene_data).returning(GeneTable.c.gene_id, GeneTable.c.gene_name)
                result = connection.execute(stmt)
                gene_map = {row.gene_name: row.gene_id for row in result}

        transcript_map = {}
        if not df_transcript.empty:
            df_transcript['gene_id'] = df_transcript['gtf_gene_id'].map(gene_map)
            df_transcript_insert = df_transcript[['transcript_name', 'start', 'end', 'gene_id', 'annot']].dropna(
                subset=['gene_id'])
            df_transcript_insert['gene_id'] = df_transcript_insert['gene_id'].astype(int)
            if not df_transcript_insert.empty:
                transcript_data = df_transcript_insert.to_dict('records')
                stmt = insert(TranscriptTable).values(transcript_data).returning(TranscriptTable.c.transcript_id,
                                                                                 TranscriptTable.c.transcript_name)
                result = connection.execute(stmt)
                transcript_map = {row.transcript_name: row.transcript_id for row in result}

        exon_map = {}
        if not df_exon.empty:
            df_exon['transcript_id'] = df_exon['gtf_transcript_id'].map(transcript_map)
            df_exon_insert = df_exon[['exon_name', 'start', 'end', 'exon_rank', 'transcript_id']].dropna(
                subset=['transcript_id'])
            df_exon_insert['transcript_id'] = df_exon_insert['transcript_id'].astype(int)
            if not df_exon_insert.empty:
                exon_data = df_exon_insert.to_dict('records')
                stmt = insert(ExonTable).values(exon_data).returning(
                    ExonTable.c.exon_id, ExonTable.c.transcript_id,
                    ExonTable.c.start, ExonTable.c.end
                )
                result = connection.execute(stmt)
                df_exon_db = pd.DataFrame(result.fetchall(), columns=['exon_id', 'transcript_id', 'start', 'end'])
                df_exon_merged = pd.merge(
                    df_exon[['temp_exon_id', 'transcript_id', 'start', 'end']],
                    df_exon_db, on=['transcript_id', 'start', 'end'], how='inner'
                )
                # Silently ignore mismatches if any, or add error handling if needed
                exon_map = pd.Series(df_exon_merged.exon_id.values, index=df_exon_merged.temp_exon_id).to_dict()

    feature_dfs = {
        'cds': (df_cds, CdsTable),
        'three_utr': (df_three_utr, ThreeUTRTable),
        'five_utr': (df_five_utr, FiveUTRTable),
    }
    for feature_name, (df_feature, table_obj) in feature_dfs.items():
        if not df_feature.empty:
            df_feature['exon_id'] = df_feature['temp_exon_id'].map(exon_map)
            cols_to_insert = ['start', 'end', 'exon_id']
            if feature_name == 'cds':
                cols_to_insert.insert(0, 'cds_name')
            df_feature_insert = df_feature[cols_to_insert].dropna(subset=['exon_id'])
            if not df_feature_insert.empty:
                df_feature_insert['exon_id'] = df_feature_insert['exon_id'].astype(int)
                if 'cds_name' in df_feature_insert.columns:
                    df_feature_insert['cds_name'] = df_feature_insert['cds_name'].where(
                        pd.notna(df_feature_insert['cds_name']), None)
                df_feature_insert.to_sql(table_obj.name, connection, if_exists='append', index=False)

    if not df_intron.empty:
        df_intron['transcript_id'] = df_intron['gtf_transcript_id'].map(transcript_map)
        df_intron_insert = df_intron[['transcript_id', 'intron_rank', 'start', 'end']].dropna(subset=['transcript_id'])
        if not df_intron_insert.empty:
            df_intron_insert['transcript_id'] = df_intron_insert['transcript_id'].astype(int)
            # this is the last one so just being lazy here
            df_intron_insert.to_sql("introns", connection, if_exists='append', index=False)

    transaction.commit()
    return None




