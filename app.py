import streamlit as st
import pandas as pd
import altair as alt

# Judul Aplikasi
st.title("Analisa Success Rate Booking period Maret - Oktober")

# Upload file CSV dari komputer
uploaded_file = st.file_uploader("Pilih file CSV", type="csv")

if uploaded_file is not None:
    # Membaca file CSV ke dalam DataFrame
    df = pd.read_csv(uploaded_file, delimiter=';')

    # Membersihkan kolom 'Unnamed' jika ada
    df = df.drop(columns=[col for col in df.columns if 'Unnamed' in col], errors='ignore')

    # Tampilkan dataset asli tanpa modifikasi
    st.write("Dataset Customer")
    st.dataframe(df)

    # Membuat DataFrame baru untuk menampilkan nama kolom dan tipe data
    column_info = {
        'Tipe Data': df.dtypes.astype(str)
    }
    
    df_column_info = pd.DataFrame(column_info)

    # Menghitung jumlah kolom Level 1 time yang terisi
    level_1_filled = df['Level 1 time'].notna().sum()
    
    # Menghitung jumlah kolom Level 3 time yang terisi
    level_3_filled = df['Level 3 time'].notna().sum()
    
    # Menghitung jumlah kolom Level 3 time yang kosong
    level_3_empty = df['Level 3 time'].isna().sum()

    # Menghitung rata-rata dari kolom Selisih Hari dari Leads Hingga Booking
    avg_days_diff = df['Selisih Hari dari Leads Hingga Booking'].mean()

    # Menghitung jumlah customer yang belum booking di kolom Level 3
    belum_booking_level_3 = df[df['Keterangan Booking'] == 'Belum Booking'].shape[0]

    # Menghitung persentase customer yang belum booking dari jumlah Level 1 time yang terisi
    if level_1_filled > 0:
        belum_booking_percentage = (belum_booking_level_3 / level_1_filled) * 100
    else:
        belum_booking_percentage = 0

    # Membuat DataFrame untuk menampilkan hasil
    summary_data = {
        'Keterangan': [
            'Customer Mengisi Leads', 
            'Customer Melakukan Booking', 
            'Customer Belum Booking', 
            'Rata-rata Selisih Hari dari Leads Hingga Booking (Hari)',
            'Persentase Customer yang Belum Booking (%)'
        ],
        'Jumlah': [level_1_filled, level_3_filled, level_3_empty, avg_days_diff, belum_booking_percentage]
    }
    
    df_summary = pd.DataFrame(summary_data)

    # Tampilkan DataFrame hasil perhitungan
    st.write("Total Customer yang mengisi Leads, Total Customer Yang Sudah Melakukan Booking, Total Customer Yang Belum Melakukan Booking, Rata Rata Selisih Hari Dari Leads Hingga Booking, dan Presentase Customer Yang Belum Sampai Tahap Booking")
    st.dataframe(df_summary)

    # Pembagian kelompok berdasarkan selisih hari dari Leads hingga Booking
    df['Pembagian Kelompok Customer'] = pd.cut(df['Selisih Hari dari Leads Hingga Booking'], 
                                               bins=[0, 5, 10, float('inf')], 
                                               labels=['<5 Hari', '5-10 Hari', '>10 Hari'], 
                                               include_lowest=True)

    # Menghitung jumlah customer berdasarkan kelompok
    booking_groups = df['Pembagian Kelompok Customer'].value_counts().reindex(['<5 Hari', '5-10 Hari', '>10 Hari'], fill_value=0)

    # Membuat DataFrame baru untuk kelompok customer
    booking_group_data = {
        'Selisih Waktu': booking_groups.index,
        'Jumlah Customer': booking_groups.values
    }
    
    df_booking_groups = pd.DataFrame(booking_group_data)

    # Tampilkan DataFrame hasil perhitungan kelompok customer
    st.write("Jumlah Customer Berdasarkan Pembagian Selisih Waktu dari Leads Ke Booking:")
    st.dataframe(df_booking_groups)

    # Menambahkan bagian grafik ke dalam expander
    with st.expander("Lihat Grafik Korelasi Antara Sumber dan Transisi Kelompok Customer dari Leads ke Booking Berdasarkan Waktu Transisi"):
        # Menghitung jumlah data berdasarkan kolom Sumber dan Transisi Kelompok Customer dari Leads Ke Booking
        correlation_data_transisi = df.groupby(['Sumber', 'Pembagian Kelompok Customer']).size().reset_index(name='Jumlah')

        # Membuat chart untuk kelompok <5 Hari
        transisi_data_5_hari = correlation_data_transisi[correlation_data_transisi['Pembagian Kelompok Customer'] == '<5 Hari']
        chart_5_hari = alt.Chart(transisi_data_5_hari).mark_bar().encode(
            y=alt.Y('Sumber:N', axis=alt.Axis(title='Sumber')),  # Sumber pada sumbu Y
            x=alt.X('Jumlah:Q', axis=alt.Axis(title='Jumlah Customer')),  # Jumlah pada sumbu X
            color=alt.value('green'),  # Warna batang untuk <5 Hari
            tooltip=['Sumber:N', 'Jumlah:Q']  # Tooltip
        ).properties(
            title='Jumlah Customer dengan Transisi <5 Hari dari Leads ke Booking',  # Judul chart
            width=1000,  # Lebar chart
            height=650  # Tinggi chart
        ).interactive()

        # Menambahkan label di atas batang untuk <5 Hari
        text_5_hari = chart_5_hari.mark_text(
            align='left',
            baseline='middle',
            dx=3  # Offset horizontal untuk teks
        ).encode(
            x='Jumlah:Q',  # Menggunakan Jumlah sebagai posisi x
            y='Sumber:N',
            text='Jumlah:Q'  # Menampilkan jumlah sebagai label
        )

        # Membuat chart untuk kelompok 5-10 Hari
        transisi_data_5_10_hari = correlation_data_transisi[correlation_data_transisi['Pembagian Kelompok Customer'] == '5-10 Hari']
        chart_5_10_hari = alt.Chart(transisi_data_5_10_hari).mark_bar().encode(
            y=alt.Y('Sumber:N', axis=alt.Axis(title='Sumber')),  # Sumber pada sumbu Y
            x=alt.X('Jumlah:Q', axis=alt.Axis(title='Jumlah Customer')),  # Jumlah pada sumbu X
            color=alt.value('blue'),  # Warna batang untuk 5-10 Hari
            tooltip=['Sumber:N', 'Jumlah:Q']  # Tooltip
        ).properties(
            title='Jumlah Customer dengan Transisi 5-10 Hari dari Leads ke Booking',  # Judul chart
            width=1000,  # Lebar chart
            height=650  # Tinggi chart
        ).interactive()

        # Menambahkan label di atas batang untuk 5-10 Hari
        text_5_10_hari = chart_5_10_hari.mark_text(
            align='left',
            baseline='middle',
            dx=3  # Offset horizontal untuk teks
        ).encode(
            x='Jumlah:Q',  # Menggunakan Jumlah sebagai posisi x
            y='Sumber:N',
            text='Jumlah:Q'  # Menampilkan jumlah sebagai label
        )

        # Membuat chart untuk kelompok >10 Hari
        transisi_data_10_hari = correlation_data_transisi[correlation_data_transisi['Pembagian Kelompok Customer'] == '>10 Hari']
        chart_10_hari = alt.Chart(transisi_data_10_hari).mark_bar().encode(
            y=alt.Y('Sumber:N', axis=alt.Axis(title='Sumber')),  # Sumber pada sumbu Y
            x=alt.X('Jumlah:Q', axis=alt.Axis(title='Jumlah Customer')),  # Jumlah pada sumbu X
            color=alt.value('red'),  # Warna batang untuk >10 Hari
            tooltip=['Sumber:N', 'Jumlah:Q']  # Tooltip
        ).properties(
            title='Jumlah Customer dengan Transisi >10 Hari dari Leads ke Booking',  # Judul chart
            width=1000,  # Lebar chart
            height=650  # Tinggi chart
        ).interactive()

        # Menambahkan label di atas batang untuk >10 Hari
        text_10_hari = chart_10_hari.mark_text(
            align='left',
            baseline='middle',
            dx=3  # Offset horizontal untuk teks
        ).encode(
            x='Jumlah:Q',  # Menggunakan Jumlah sebagai posisi x
            y='Sumber:N',
            text='Jumlah:Q'  # Menampilkan jumlah sebagai label
        )

        # Gabungkan semua chart dan tampilkan di Streamlit secara berurutan (vertikal)
        st.altair_chart(chart_5_hari + text_5_hari)
        st.altair_chart(chart_5_10_hari + text_5_10_hari)
        st.altair_chart(chart_10_hari + text_10_hari)

    # Menghitung jumlah pengisian leads saat Weekday dan Weekend
    weekday_leads_count = df[df['Waktu Leads'] == 'Weekday'].shape[0]
    weekend_leads_count = df[df['Waktu Leads'] == 'Weekend'].shape[0]

    # Membuat DataFrame untuk pengisian leads
    leads_data = {
        'Keterangan': ['Jumlah Pengisian Leads Saat Weekday', 'Jumlah Pengisian Leads Saat Weekend'],
        'Jumlah': [weekday_leads_count, weekend_leads_count]
    }
    
    df_leads_summary = pd.DataFrame(leads_data)

    # Menghitung jumlah booking saat Weekday dan Weekend
    weekday_booking_count = df[df['Waktu Booking'] == 'Weekday'].shape[0]
    weekend_booking_count = df[df['Waktu Booking'] == 'Weekend'].shape[0]

    # Membuat DataFrame untuk booking
    booking_data = {
        'Keterangan': ['Jumlah Booking Saat Weekday', 'Jumlah Booking Saat Weekend'],
        'Jumlah': [weekday_booking_count, weekend_booking_count]
    }
    
    df_booking_summary = pd.DataFrame(booking_data)

    # Tampilkan DataFrame untuk pengisian leads
    st.write("Jumlah Pengisian Leads saat Weekday dan Weekend:")
    st.dataframe(df_leads_summary)

    # Menghitung jumlah data berdasarkan kolom Sumber dan Waktu Leads
    correlation_data_leads = df.groupby(['Sumber', 'Waktu Leads']).size().reset_index(name='Jumlah')

    # Buat tombol untuk show/hide chart leads
    with st.expander("Tampilkan Grafik Korelasi Sumber Informasi dengan Waktu Leads"):
        # Membuat chart untuk Weekday
        weekday_data = correlation_data_leads[correlation_data_leads['Waktu Leads'] == 'Weekday']
        chart_weekday = alt.Chart(weekday_data).mark_bar().encode(
            y=alt.Y('Sumber:N', axis=alt.Axis(title='Sumber')),  # Sumber pada sumbu Y
            x=alt.X('Jumlah:Q', axis=alt.Axis(title='Jumlah Customer')),  # Jumlah pada sumbu X
            color=alt.value('steelblue'),  # Warna batang untuk Weekday
            tooltip=['Sumber:N', 'Jumlah:Q']  # Tooltip
        ).properties(
            title='Jumlah Sumber Yang Menarik Customer Untuk Mengisi Leads Saat Weekday',  # Judul chart
            width=1000,  # Lebar chart
            height=650  # Tinggi chart
        ).interactive()  # Menambahkan interaktivitas jika diperlukan

        # Menambahkan label di atas batang
        text_weekday = chart_weekday.mark_text(
            align='left',
            baseline='middle',
            dx=3  # Offset horizontal untuk teks
        ).encode(
            x='Jumlah:Q',  # Menggunakan Jumlah sebagai posisi x
            y='Sumber:N',
            text='Jumlah:Q'  # Menampilkan jumlah sebagai label
        )

        # Membuat chart untuk Weekend
        weekend_data = correlation_data_leads[correlation_data_leads['Waktu Leads'] == 'Weekend']
        chart_weekend = alt.Chart(weekend_data).mark_bar().encode(
            y=alt.Y('Sumber:N', axis=alt.Axis(title='Sumber')),  # Sumber pada sumbu Y
            x=alt.X('Jumlah:Q', axis=alt.Axis(title='Jumlah Customer')),  # Jumlah pada sumbu X
            color=alt.value('orange'),  # Warna batang untuk Weekend
            tooltip=['Sumber:N', 'Jumlah:Q']  # Tooltip
        ).properties(
            title='Jumlah Sumber Yang Menarik Customer Untuk Mengisi Leads Saat Weekend',  # Judul chart
            width=1000,  # Lebar chart
            height=650  # Tinggi chart
        ).interactive()  # Menambahkan interaktivitas jika diperlukan

        # Menambahkan label di atas batang
        text_weekend = chart_weekend.mark_text(
            align='left',
            baseline='middle',
            dx=3  # Offset horizontal untuk teks
        ).encode(
            x='Jumlah:Q',  # Menggunakan Jumlah sebagai posisi x
            y='Sumber:N',
            text='Jumlah:Q'  # Menampilkan jumlah sebagai label
        )

        # Gabungkan chart dengan label
        combined_weekday_chart = chart_weekday + text_weekday
        combined_weekend_chart = chart_weekend + text_weekend

        # Tampilkan kedua chart di Streamlit secara berurutan (vertikal)
        st.altair_chart(combined_weekday_chart)
        st.altair_chart(combined_weekend_chart)

    # Tampilkan DataFrame untuk booking
    st.write("Jumlah Booking saat Weekday dan Weekend:")
    st.dataframe(df_booking_summary)

    # Menghitung jumlah data berdasarkan kolom Sumber dan Waktu Booking
    correlation_data_booking = df.groupby(['Sumber', 'Waktu Booking']).size().reset_index(name='Jumlah')

    # Buat tombol untuk show/hide chart booking
    with st.expander("Tampilkan Grafik Korelasi Sumber Informasi dengan Waktu Booking"):
        # Membuat chart untuk Weekday Booking
        weekday_booking_data = correlation_data_booking[correlation_data_booking['Waktu Booking'] == 'Weekday']
        chart_weekday_booking = alt.Chart(weekday_booking_data).mark_bar().encode(
            y=alt.Y('Sumber:N', axis=alt.Axis(title='Sumber')),  # Sumber pada sumbu Y
            x=alt.X('Jumlah:Q', axis=alt.Axis(title='Jumlah Customer')),  # Jumlah pada sumbu X
            color=alt.value('steelblue'),  # Warna batang untuk Weekday
            tooltip=['Sumber:N', 'Jumlah:Q']  # Tooltip
        ).properties(
            title='Jumlah Sumber Yang Menarik Customer Untuk Booking Saat Weekday',  # Judul chart
            width=1000,  # Lebar chart
            height=650  # Tinggi chart
        ).interactive()  # Menambahkan interaktivitas jika diperlukan

        # Menambahkan label di atas batang
        text_weekday_booking = chart_weekday_booking.mark_text(
            align='left',
            baseline='middle',
            dx=3  # Offset horizontal untuk teks
        ).encode(
            x='Jumlah:Q',  # Menggunakan Jumlah sebagai posisi x
            y='Sumber:N',
            text='Jumlah:Q'  # Menampilkan jumlah sebagai label
        )

        # Membuat chart untuk Weekend Booking
        weekend_booking_data = correlation_data_booking[correlation_data_booking['Waktu Booking'] == 'Weekend']
        chart_weekend_booking = alt.Chart(weekend_booking_data).mark_bar().encode(
            y=alt.Y('Sumber:N', axis=alt.Axis(title='Sumber')),  # Sumber pada sumbu Y
            x=alt.X('Jumlah:Q', axis=alt.Axis(title='Jumlah Customer')),  # Jumlah pada sumbu X
            color=alt.value('orange'),  # Warna batang untuk Weekend
            tooltip=['Sumber:N', 'Jumlah:Q']  # Tooltip
        ).properties(
            title='Jumlah Sumber Yang Menarik Customer Untuk Booking Saat Weekend',  # Judul chart
            width=1000,  # Lebar chart
            height=650  # Tinggi chart
        ).interactive()  # Menambahkan interaktivitas jika diperlukan

        # Menambahkan label di atas batang
        text_weekend_booking = chart_weekend_booking.mark_text(
            align='left',
            baseline='middle',
            dx=3  # Offset horizontal untuk teks
        ).encode(
            x='Jumlah:Q',  # Menggunakan Jumlah sebagai posisi x
            y='Sumber:N',
            text='Jumlah:Q'  # Menampilkan jumlah sebagai label
        )

        # Gabungkan chart dengan label
        combined_weekday_booking_chart = chart_weekday_booking + text_weekday_booking
        combined_weekend_booking_chart = chart_weekend_booking + text_weekend_booking

        # Tampilkan kedua chart di Streamlit secara berurutan (vertikal)
        st.altair_chart(combined_weekday_booking_chart)
        st.altair_chart(combined_weekend_booking_chart)

else:
    st.write("Silakan upload file CSV.")
