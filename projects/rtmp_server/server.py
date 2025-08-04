import asyncio
from lk_utils import run_cmd_args
from lk_utils import xpath
from pyrtmp import StreamClosedException
from pyrtmp.flv import FLVFileWriter
from pyrtmp.flv import FLVMediaType
from pyrtmp.rtmp import RTMPProtocol
from pyrtmp.rtmp import SimpleRTMPController
from pyrtmp.rtmp import SimpleRTMPServer
from pyrtmp.session_manager import SessionManager

ffmpeg_bin = 'C:/Likianta/apps/ffmpeg/bin/ffmpeg.exe'


class RtmpToFlvController(SimpleRTMPController):
    
    def __init__(self) -> None:
        self.output_directory = xpath('records')
        self._session_to_file = {}
        super().__init__()
    
    async def on_ns_publish(self, session, message) -> None:
        file = '{}/{}.flv'.format(
            self.output_directory, message.publishing_name
        )
        print(file, ':v2')
        writer = FLVFileWriter(file)
        writer.filepath = file
        session.state = writer
        await super().on_ns_publish(session, message)
    
    async def on_metadata(self, session, message) -> None:
        session.state.write(
            0, message.to_raw_meta(), FLVMediaType.OBJECT
        )
        await super().on_metadata(session, message)
    
    async def on_video_message(self, session, message) -> None:
        session.state.write(
            message.timestamp, message.payload, FLVMediaType.VIDEO
        )
        await super().on_video_message(session, message)
    
    async def on_audio_message(self, session, message) -> None:
        session.state.write(
            message.timestamp, message.payload, FLVMediaType.AUDIO
        )
        await super().on_audio_message(session, message)
    
    async def on_stream_closed(
        self, session: SessionManager, exception: StreamClosedException
    ) -> None:
        filepath = session.state.filepath
        session.state.close()
        await super().on_stream_closed(session, exception)
        print('stream closed', filepath, ':t0s')
        run_cmd_args(
            ffmpeg_bin,
            '-i', filepath,
            filepath.replace('.flv', '.mp4'),
            '-y',
            verbose=True,
        )
        print('convert flv to mp4 done', ':t')


class SimpleServer(SimpleRTMPServer):
    async def create(self, host: str, port: int):
        loop = asyncio.get_event_loop()
        self.server = await loop.create_server(
            lambda: RTMPProtocol(controller=RtmpToFlvController()),
            host=host,
            port=port,
        )


async def main() -> None:
    server = SimpleServer()
    await server.create(host='0.0.0.0', port=2014)
    await server.start()
    await server.wait_closed()


if __name__ == '__main__':
    # 1. pox projects/rtmp_server/server.py
    # 2. bore ... -p 2014 2014
    # 3. dji mimo: rtmp://47.102.108.149:2014/test/sample
    # 4. file will be saved in `/projects/rtmp_server/records/sample.flv`
    asyncio.run(main())
